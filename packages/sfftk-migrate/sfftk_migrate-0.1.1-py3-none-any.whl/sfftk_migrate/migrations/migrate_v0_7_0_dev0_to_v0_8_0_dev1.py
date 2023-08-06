import base64
import struct

from lxml import etree

from .. import ENDIANNESS, MODE
from ..migrate import migrate_by_stylesheet
from ..utils import _print


def migrate_mesh(mesh, vertices_mode="float32", triangles_mode="uint32", endianness="little"):
    """Given a mesh from the v0.7.0.dev0 we convert it to a mesh in v0.8.0.dev1"""
    # assertions
    try:
        assert endianness in ["little", "big"]
    except AssertionError:
        raise ValueError("invalid endianness: {}".format(endianness))
    try:
        assert triangles_mode in ["int8", "uint8", "int16", "uint16", "int32", "uint32", "int64", "uint64"]
    except AssertionError:
        raise ValueError("invalid triangles mode: {}".format(triangles_mode))
    try:
        assert vertices_mode in ["float32", "float64"]
    except AssertionError:
        raise ValueError("invalid vertices mode: {}".format(vertices_mode))

    surface_vertex_dict = dict()  # dictionary to remap vertex ids
    surface_vertices = list()
    normal_vertices = list()
    try:
        vertex_list = next(mesh.iter("vertexList"))
    except StopIteration:
        # no geometry
        return (
            etree.Element("vertices", num_vertices="0", mode=vertices_mode, endianness=endianness, data=""),
            etree.Element("normals", num_normals="0", mode=vertices_mode, endianness=endianness, data=""),
            etree.Element("triangles", num_triangles="0", mode=triangles_mode, endianness=endianness, data="")
        )
    i = 0
    for vertex in vertex_list.iter("v"):
        designation = vertex.get("designation")
        x, y, z = vertex.xpath("*")
        # 'surface' vertex by default
        if designation is None or designation == "surface":
            surface_vertex_dict[int(vertex.get("vID"))] = len(surface_vertices) // 3  # len = index
            surface_vertices += [float(x.text), float(y.text), float(z.text)]
        else:
            normal_vertices += [float(x.text), float(y.text), float(z.text)]
    # _print(surface_vertex_dict)
    # sanity check: normal_vertices should have the same length as surface_vertices list if it exists
    if normal_vertices:
        try:
            assert len(surface_vertices) == len(normal_vertices)
        except AssertionError:
            raise ValueError("surface and normal vertice lists are of different length")
    bin_surface_vertices = struct.pack(
        "{}{}{}".format(ENDIANNESS[endianness], len(surface_vertices), MODE[vertices_mode]), *surface_vertices)
    base64_surface_vertices = base64.b64encode(bin_surface_vertices)
    bin_normal_vertices = struct.pack(
        "{}{}{}".format(ENDIANNESS[endianness], len(normal_vertices), MODE[vertices_mode]), *normal_vertices)
    base64_normal_vertices = base64.b64encode(bin_normal_vertices)
    surface_vertices_element = etree.Element("vertices", num_vertices=str(len(surface_vertices) // 3),
                                             mode=vertices_mode,
                                             endianness=endianness, data=base64_surface_vertices)
    surface_vertices_element.tail = "\n\t\t\t\t\t"
    normal_vertices_element = etree.Element("normals", num_normals=str(len(normal_vertices) // 3), mode=vertices_mode,
                                            endianness=endianness, data=base64_normal_vertices)
    normal_vertices_element.tail = "\n\t\t\t\t\t"

    # work on triangles
    triangles = list()
    triangle_list = next(mesh.iter("polygonList"))
    for triangle in triangle_list.iter("P"):
        vertex_indices = triangle.xpath("*")
        if len(vertex_indices) == 3:  # no normals
            _v1, _v2, _v3 = vertex_indices
            v1 = int(_v1.text)
            v2 = int(_v2.text)
            v3 = int(_v3.text)
        elif len(vertex_indices) == 6:  # s, n, s, n, s, n
            _v1, _n1, _v2, _n2, _v3, _n3 = vertex_indices
            # get the new index
            v1 = surface_vertex_dict[int(_v1.text)]
            v2 = surface_vertex_dict[int(_v2.text)]
            v3 = surface_vertex_dict[int(_v3.text)]
        else:
            raise ValueError("invalid polygon: should have 3 or 6 vertices only")

        triangles += [v1, v2, v3]
    # sanity check: there should be no triangle with a vertex id larger than the length of vertices/normals
    try:
        assert max(triangles) < len(surface_vertices)
    except AssertionError:
        raise ValueError("triangle with non-existent vertex found!")
    bin_triangles = struct.pack("{}{}{}".format(ENDIANNESS[endianness], len(triangles), MODE[triangles_mode]),
                                *triangles)
    base64_triangles = base64.b64encode(bin_triangles)
    triangles_element = etree.Element("triangles", num_triangles=str(len(triangles) // 3), mode=triangles_mode,
                                      endianness=endianness, data=base64_triangles)
    triangles_element.tail = "\n\t\t\t\t"

    return surface_vertices_element, normal_vertices_element, triangles_element


def migrate(infile, outfile, stylesheet, args, encoding='utf-8', **kwargs):
    if args.verbose:
        _print("migrating by stylesheet...")
    _migrated = migrate_by_stylesheet(infile, stylesheet, verbose=args.verbose, **kwargs)

    if args.verbose:
        _print("ad hoc migration by function...")
    # convert migration to an ElementTree object
    migrated = etree.ElementTree(etree.XML(_migrated))

    _original = etree.parse(infile)

    segments = _original.xpath('/segmentation/segmentList/segment')
    # _print(segments)
    segment_meshes = dict()
    for segment in segments:
        segment_meshes[int(segment.get("id"))] = dict()
        for mesh in segment.xpath('meshList/mesh'):
            _vertices, _normals, _triangles = migrate_mesh(mesh)
            segment_meshes[int(segment.get("id"))][int(mesh.get("id"))] = _vertices, _normals, _triangles

    migrated_segments = migrated.xpath('/segmentation/segment_list/segment')
    for migrated_segment in migrated_segments:
        for migrated_mesh in migrated_segment.xpath('mesh_list/mesh'):
            _vertices, _normals, _triangles = segment_meshes[int(migrated_segment.get("id"))][
                int(migrated_mesh.get("id"))]
            migrated_mesh.insert(0, _vertices)
            migrated_mesh.insert(1, _normals)
            migrated_mesh.insert(2, _triangles)

    migrated_decoded = etree.tostring(migrated, xml_declaration=True, encoding=encoding, pretty_print=True).decode(
        encoding)

    if args.verbose:
        _print("writing output to {}...".format(outfile))
    with open(outfile, 'w') as f:
        f.write(migrated_decoded)
    if args.verbose:
        _print("done")
    return outfile
