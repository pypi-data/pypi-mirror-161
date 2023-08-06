# -*- coding: utf-8 -*-
import inspect
import os
import sys
import types
import unittest

from lxml import etree

from . import XSL, XML, VERSION_LIST
from .core import get_module, get_stylesheet, get_source_version, get_migration_path, list_versions
from .main import parse_args
from .migrate import migrate_by_stylesheet, do_migration, get_params
from .utils import _print, _check, _decode_data

replace_list = [
    ('\n', ''),
    ('\t', ''),
    (' ', ''),
]


def _replace(s, vals=replace_list):
    if s is None:
        return ''
    _s = s
    for u, v in vals:
        _s = _s.replace(u, v)
    return _s


def compare_elements(el1, el2):
    """Compare two elements and all their children

    :return: True or False
    """
    _check(el1, (etree._Element), TypeError)
    _check(el2, (etree._Element), TypeError)
    # https://stackoverflow.com/questions/7905380/testing-equivalence-of-xml-etree-elementtree
    if el1.tag != el2.tag:
        return False
    if _replace(el1.text) != _replace(el2.text):
        return False
    if _replace(el1.tail) != _replace(el2.tail):
        return False
    if el1.attrib != el2.attrib:
        return False
    if len(el1) != len(el2):
        return False
    return all(compare_elements(e1, e2) for e1, e2 in zip(el1, el2))


class TestUtils(unittest.TestCase):
    def test_check(self):
        """Test that _check works"""
        with self.assertRaisesRegex(TypeError, r"object '1' is not of class <class 'str'>"):
            _check(1, str, TypeError)
        with self.assertRaises(TypeError):
            _check(1, str, TypeError, message="")

    def test_migrate(self):
        """Test that migrate works"""

        # exceptions
        with self.assertRaises(TypeError):
            migrate_by_stylesheet(1, 2)
        with self.assertRaises(IOError):
            migrate_by_stylesheet('file.xml', 'file.xsl')

    def test_parse_args(self):
        """Test correct arguments"""
        # default with -t/--target-version
        args = parse_args("file.xml -v -t 1.0")
        self.assertEqual(args.infile, "file.xml")
        self.assertEqual(args.target_version, "1.0")
        self.assertEqual(args.outfile, "file_v1.0.xml")
        self.assertFalse(args.list_versions)
        # specify outfile
        args = parse_args("file.xml -v -t 1.0 -o my_output.xml")
        self.assertEqual(args.outfile, "my_output.xml")
        # list valid versions
        args = parse_args("-l")
        self.assertEqual(args.infile, '')
        self.assertEqual(args.target_version, VERSION_LIST[-1])
        self.assertIsNone(args.outfile)
        self.assertTrue(args.list_versions)
        self.assertFalse(args.show_version)
        # show version in file
        args = parse_args("-v -s file.xml")
        self.assertEqual(args.infile, 'file.xml')
        self.assertEqual(args.target_version, VERSION_LIST[-1])
        # self.assertEqual(args.outfile, 'file_v0.8.0.dev1.xml')
        self.assertIsNone(args.outfile)
        self.assertFalse(args.list_versions)
        self.assertTrue(args.show_version)
        # show package version
        args = parse_args("-v -V")
        self.assertEqual(args.infile, '')
        self.assertIsNone(args.outfile)
        self.assertTrue(args.version)
        self.assertFalse(args.list_versions)
        self.assertFalse(args.show_version)

    def test_get_stylesheet(self):
        """Given versions return the correct stylesheet to use"""
        stylesheet = get_stylesheet("1", "2")
        self.assertEqual(os.path.basename(stylesheet), 'migrate_v1_to_v2.xsl')
        self.assertTrue(os.path.exists(stylesheet))
        original = os.path.join(XML, 'original.xml')
        _migrated = migrate_by_stylesheet(original, stylesheet,
                                          segmentation_details="Nothing much")
        migrated = etree.ElementTree(etree.XML(_migrated))
        sys.stderr.write('migrated:\n' + etree.tostring(migrated).decode('utf-8'))
        # self.assertTrue(False)
        with self.assertRaises(OSError):
            get_stylesheet("nothing", "something")

    def test_get_source_version(self):
        """Obtain the version in the original"""
        source_version = get_source_version(os.path.join(XML, 'original.xml'))
        self.assertEqual(source_version, '1')
        fn_v07 = os.path.join(XML, 'test2.sff')
        source_version_v07 = get_source_version(fn_v07)
        self.assertEqual(source_version_v07, '0.7.0.dev0')
        fn_v08 = os.path.join(XML, 'test2_v0.8.0.dev1.sff')
        source_version_v08 = get_source_version(fn_v08)
        self.assertEqual(source_version_v08, '0.8.0.dev1')

    def test_get_migration_path(self):
        """Determine the sequence of migrations to perform"""
        version_list = ['1', '2', '3', '4', '5', '6']
        migration_path = get_migration_path('2', '6', version_list=version_list)
        self.assertEqual(migration_path, [('2', '3'), ('3', '4'), ('4', '5'), ('5', '6')])
        # cannot find start
        with self.assertRaisesRegex(ValueError, r".*invalid migration start.*"):
            get_migration_path('0', '6', version_list=version_list)
        # cannot find end
        with self.assertRaisesRegex(ValueError, r".*invalid migration end.*"):
            get_migration_path('1', '9', version_list=version_list)

    def test_do_migration_example(self):
        """Toy migration example"""
        version_list = ['1', '2']
        cmd = "{infile} -v --target-version 2 --outfile {outfile}".format(
            infile=os.path.join(XML, "original.xml"),
            outfile=os.path.join(XML, "my_output.xml")
        )
        args = parse_args(cmd)
        _text = "48ec3e2ab568763658fc3f5430b851ceaf1593d6"  # secrets.token_hex(20)
        status = do_migration(
            args,
            value_list=[_text],
            version_list=version_list,
        )
        _output = os.path.join(XML, "original_v2.xml")
        self.assertTrue(os.path.exists(_output))
        self.assertEqual(status, os.EX_OK)
        output = etree.parse(_output)
        self.assertEqual(output.xpath('/segmentation/details/text()')[0], _text)
        os.remove(args.outfile)

    def test_do_migration(self):
        """Do an actual migration using the convenience function"""
        # try a null migration
        target_version = "0.8.0.dev1"
        outfile = os.path.join(XML, 'my_file_out.sff')
        cmd = "{infile} -v --target-version {target_version} --outfile {outfile}".format(
            infile=os.path.join(XML, 'test2_v0.8.0.dev1.sff'),
            target_version=target_version,
            outfile=outfile,
        )
        args = parse_args(cmd)
        status = do_migration(args)
        self.assertEqual(status, os.EX_OK)
        self.assertFalse(os.path.exists(outfile))  # the file was not created
        # try an actual migrations
        cmd = "{infile} -v --target-version {target_version} --outfile {outfile}".format(
            infile=os.path.join(XML, 'test2.sff'),
            target_version=target_version,
            outfile=outfile
        )
        args = parse_args(cmd)
        status = do_migration(args)
        self.assertEqual(status, os.EX_OK)
        self.assertTrue(os.path.exists(outfile))  # the file was not created
        in_version = get_source_version(args.infile)
        out_version = get_source_version(outfile)
        self.assertNotEqual(in_version, out_version)
        self.assertEqual(out_version, target_version)
        os.remove(outfile)

    def test_do_migration_fail_missing_file(self):
        """Print an error message if the file does not exist"""
        target_version = "0.8.0.dev1"
        outfile = 'my_file_out.sff'  # incorrect path
        cmd = "{infile} -v --target-version {target_version} --outfile {outfile}".format(
            infile='test2_v0.8.0.dev1.sff',  # non-existent file
            target_version=target_version,
            outfile=outfile,
        )
        args = parse_args(cmd)
        status = do_migration(args)
        self.assertEqual(status, os.EX_IOERR)

    def test_get_module(self):
        """Check that we can get the right module for this migration"""
        module = get_module('1', '2')
        self.assertIsInstance(module, types.ModuleType)

    def test_get_params(self):
        """Test getting params"""
        module = get_module('1', '2')
        _text = "ce3c90151bb3c803c8e6570ee7d5845ac3c96c38"  # secrets.token_hex(20)
        params = get_params(module.PARAM_LIST, value_list=[_text])
        self.assertIsInstance(params, dict)
        self.assertEqual(len(params), 1)
        with self.assertRaises(ValueError):
            get_params(module.PARAM_LIST, value_list=[_text, _text])

    def test_list_versions(self):
        """Test that we can list the supported versions"""
        args = parse_args("-v -l")
        status, version_count = list_versions()
        self.assertEqual(status, os.EX_OK)
        self.assertEqual(version_count, 2)


class TestMigrations(unittest.TestCase):
    def test_original_to_add_field(self):
        """Test adding a field to the original"""
        original = os.path.join(XML, 'original.xml')
        reference = etree.parse(os.path.join(XML, 'add_field.xml'))
        stylesheet = os.path.join(XSL, 'original_to_add_field.xsl')
        # we pass the value of the `details` param as follows:
        # A = reference.xpath(<xpath>)[0]
        # etree.XSLT.strparam(A) - handle a possibly quoted string
        details_text = reference.xpath('/segmentation/details/text()')[0]
        _migrated = migrate_by_stylesheet(original, stylesheet,
                                          segmentation_details=details_text)  # bytes
        migrated = etree.ElementTree(etree.XML(_migrated))
        same = compare_elements(reference.getroot(), migrated.getroot())
        sys.stderr.write('reference:\n' + etree.tostring(reference).decode('utf-8'))
        sys.stderr.write('\n')
        sys.stderr.write('migrated:\n' + etree.tostring(migrated).decode('utf-8'))
        self.assertTrue(same)

    def test_original_to_drop_field(self):
        """Test dropping a field from the original"""
        original = os.path.join(XML, 'original.xml')
        reference = etree.parse(os.path.join(XML, 'drop_field.xml'))
        stylesheet = os.path.join(XSL, 'original_to_drop_field.xsl')
        with self.assertWarns(UserWarning):
            _migrated = migrate_by_stylesheet(original, stylesheet, verbose=True)
        migrated = etree.ElementTree(etree.XML(_migrated))
        same = compare_elements(reference.getroot(), migrated.getroot())
        self.assertTrue(same)
        sys.stderr.write('reference:\n' + etree.tostring(reference).decode('utf-8'))
        sys.stderr.write('\n')
        sys.stderr.write('migrated:\n' + etree.tostring(migrated).decode('utf-8'))

    def test_original_to_change_field_rename_field(self):
        """Test changing a field by renaming it"""
        original = os.path.join(XML, 'original.xml')
        reference = etree.parse(os.path.join(XML, 'change_field_rename_field.xml'))
        stylesheet = os.path.join(XSL, 'original_to_change_field_rename_field.xsl')
        _migrated = migrate_by_stylesheet(original, stylesheet)
        migrated = etree.ElementTree(etree.XML(_migrated))
        same = compare_elements(reference.getroot(), migrated.getroot())
        self.assertTrue(same)
        # sys.stderr.write('reference:\n' + etree.tostring(reference).decode('utf-8'))
        # sys.stderr.write('\n')
        # sys.stderr.write('migrated:\n' + etree.tostring(migrated).decode('utf-8'))

    def test_original_to_change_field_add_attribute(self):
        """Test changing a field by adding an attribute"""
        original = os.path.join(XML, 'original.xml')
        reference = etree.parse(os.path.join(XML, 'change_field_add_attribute.xml'))
        stylesheet = os.path.join(XSL, 'original_to_change_field_add_attribute.xsl')
        lang_text = reference.xpath('/segmentation/name/@lang')[0]
        _migrated = migrate_by_stylesheet(original, stylesheet,
                                          segmentation_name_lang=lang_text)
        migrated = etree.ElementTree(etree.XML(_migrated))
        same = compare_elements(reference.getroot(), migrated.getroot())
        self.assertTrue(same)
        # sys.stderr.write('reference:\n' + etree.tostring(reference).decode('utf-8'))
        # sys.stderr.write('\n')
        # sys.stderr.write('migrated:\n' + etree.tostring(migrated).decode('utf-8'))

    def test_original_to_change_field_drop_attribute(self):
        """Test changing a field by dropping an attribute"""
        original = os.path.join(XML, 'original.xml')
        reference = etree.parse(os.path.join(XML, 'change_field_drop_attribute.xml'))
        stylesheet = os.path.join(XSL, 'original_to_change_field_drop_attribute.xsl')
        _migrated = migrate_by_stylesheet(original, stylesheet)
        migrated = etree.ElementTree(etree.XML(_migrated))
        same = compare_elements(reference.getroot(), migrated.getroot())
        self.assertTrue(same)
        sys.stderr.write('reference:\n' + etree.tostring(reference).decode('utf-8'))
        sys.stderr.write('\n')
        sys.stderr.write('migrated:\n' + etree.tostring(migrated).decode('utf-8'))

    def test_original_to_change_field_change_value(self):
        """Test changing a field by changing the value"""
        original = os.path.join(XML, 'original.xml')
        reference = etree.parse(os.path.join(XML, 'change_field_change_value.xml'))
        stylesheet = os.path.join(XSL, 'original_to_change_field_change_value.xsl')
        _segment_name = reference.xpath('/segmentation/segment[@id=1]/name/text()')[0]
        _migrated = migrate_by_stylesheet(original, stylesheet, segment_name=_segment_name)
        migrated = etree.ElementTree(etree.XML(_migrated))
        same = compare_elements(reference.getroot(), migrated.getroot())
        sys.stderr.write('reference:\n' + etree.tostring(reference).decode('utf-8'))
        sys.stderr.write('\n')
        sys.stderr.write('migrated:\n' + etree.tostring(migrated).decode('utf-8'))
        self.assertTrue(same)

    def test_original_to_change_field_rename_attribute(self):
        """Test changing a field by renaming an attribute"""
        original = os.path.join(XML, 'original.xml')
        reference = etree.parse(os.path.join(XML, 'change_field_rename_attribute.xml'))
        stylesheet = os.path.join(XSL, 'original_to_change_field_rename_attribute.xsl')
        _migrated = migrate_by_stylesheet(original, stylesheet)
        migrated = etree.ElementTree(etree.XML(_migrated))
        same = compare_elements(reference.getroot(), migrated.getroot())
        sys.stderr.write('reference:\n' + etree.tostring(reference).decode('utf-8'))
        sys.stderr.write('\n')
        sys.stderr.write('migrated:\n' + etree.tostring(migrated).decode('utf-8'))
        self.assertTrue(same)

    def test_original_list_to_change_value_list(self):
        """Test changing all the values for a list"""
        original = os.path.join(XML, 'original_list.xml')
        reference = etree.parse(os.path.join(XML, 'change_value_list.xml'))
        stylesheet = os.path.join(XSL, 'original_to_change_value_list.xsl')
        _migrated = migrate_by_stylesheet(original, stylesheet)
        migrated = etree.ElementTree(etree.XML(_migrated))
        same = compare_elements(reference.getroot(), migrated.getroot())
        sys.stderr.write('reference:\n' + etree.tostring(reference).decode('utf-8'))
        sys.stderr.write('\n')
        sys.stderr.write('migrated:\n' + etree.tostring(migrated).decode('utf-8'))
        self.assertTrue(same)


class TestEMDBSFFMigrations(unittest.TestCase):
    def test_migrate_mesh_exceptions(self):
        """Test that we capture exceptions"""
        module = get_module('0.7.0.dev0', '0.8.0.dev1')
        # create an empty mesh
        mesh = etree.Element("mesh")
        with self.assertRaisesRegex(ValueError, r".*invalid endianness.*"):
            module.migrate_mesh(mesh, endianness='other')
        with self.assertRaisesRegex(ValueError, r".*invalid triangles mode.*"):
            module.migrate_mesh(mesh, triangles_mode='other')
        with self.assertRaisesRegex(ValueError, r".*invalid vertices mode.*"):
            module.migrate_mesh(mesh, vertices_mode='other')
        # no geometry
        verts, norms, tris = module.migrate_mesh(mesh)
        self.assertIsInstance(verts, etree._Element)
        self.assertEqual(int(verts.get("num_vertices")), 0)
        # let's get the signature of the migrate_mesh function to get the default values for kwargs
        signature = inspect.signature(module.migrate_mesh)
        # verts
        self.assertEqual(verts.get("mode"), signature.parameters['vertices_mode'].default)
        self.assertEqual(verts.get("endianness"), signature.parameters['endianness'].default)
        self.assertEqual(verts.get("data"), "")
        # norms
        self.assertEqual(norms.get("mode"), signature.parameters['vertices_mode'].default)
        self.assertEqual(norms.get("endianness"), signature.parameters['endianness'].default)
        self.assertEqual(norms.get("data"), "")
        # tris
        self.assertEqual(tris.get("mode"), signature.parameters['triangles_mode'].default)
        self.assertEqual(tris.get("endianness"), signature.parameters['endianness'].default)
        self.assertEqual(tris.get("data"), "")

    def test_v0_7_0_dev0_to_v0_8_0_dev0(self):
        """Test migration from v0.7.0.dev0 to v0.8.0.dev1"""
        original = os.path.join(XML, 'test2.sff')
        stylesheet = get_stylesheet("0.7.0.dev0", "0.8.0.dev1")
        # phase I migration using stylesheet
        _migrated = migrate_by_stylesheet(original, stylesheet)
        # convert migration to an ElementTree object
        migrated = etree.ElementTree(etree.XML(_migrated))

        _original = etree.parse(original)

        segments = _original.xpath('/segmentation/segmentList/segment')
        _print(segments)
        segment_meshes = dict()
        module = get_module('0.7.0.dev0', '0.8.0.dev1')
        for segment in segments:
            segment_meshes[int(segment.get("id"))] = dict()
            for mesh in segment.xpath('meshList/mesh'):
                _vertices, _normals, _triangles = module.migrate_mesh(
                    mesh)
                segment_meshes[int(segment.get("id"))][int(mesh.get("id"))] = _vertices, _normals, _triangles

        migrated_segments = migrated.xpath('/segmentation/segment_list/segment')
        for migrated_segment in migrated_segments:
            for migrated_mesh in migrated_segment.xpath('mesh_list/mesh'):
                _vertices, _normals, _triangles = segment_meshes[int(migrated_segment.get("id"))][
                    int(migrated_mesh.get("id"))]
                migrated_mesh.insert(0, _vertices)
                migrated_mesh.insert(1, _normals)
                migrated_mesh.insert(2, _triangles)

        # let's see what it looks like
        migrated_decoded = etree.tostring(migrated, xml_declaration=True, encoding='UTF-8', pretty_print=True).decode(
            'utf-8')
        # sys.stderr.write('migrated:\n' + migrated_decoded)
        # with open(os.path.join(XML, 'test2_v0.8.0.dev1.sff'), 'w') as f:
        #     f.write(migrated_decoded)

    def test_meshes_equal_v0_7_0_dev0_vs_v0_8_0_dev0(self):
        """Test that the mesh data is the same

        We only compare surface vertices. Normal vertices correspond one-to-one to surface vertices and are not relevant
        to triangles.
        """
        v7 = os.path.join(XML, 'test7.sff')
        v8 = os.path.join(XML, 'test7_v0.8.0.dev1.sff')
        fv7 = etree.parse(v7)
        fv8 = etree.parse(v8)
        fv7_segments = fv7.xpath('/segmentation/segmentList/segment')
        # extract vertices, normals and triangles
        fv7_segment_meshes = dict()
        for segment in fv7_segments:
            fv7_segment_meshes[int(segment.get("id"))] = dict()
            for mesh in segment.xpath('meshList/mesh'):
                fv7_segment_meshes[int(segment.get("id"))][int(mesh.get("id"))] = {
                    'surface_vertices': dict(),
                    'normal_vertices': dict(),
                    'triangles': dict(),
                }
                vertex_list = next(mesh.iter('vertexList'))
                for vertex in vertex_list:
                    if vertex.get('designation') == 'surface' or vertex.get('designation') is None:
                        fv7_segment_meshes[int(segment.get("id"))][int(mesh.get("id"))]['surface_vertices'][
                            int(vertex.get('vID'))] = tuple(map(lambda v: float(v.text), vertex.xpath('*')))
                    elif vertex.get('designation') == 'normal':
                        fv7_segment_meshes[int(segment.get("id"))][int(mesh.get("id"))]['normal_vertices'][
                            int(vertex.get('vID'))] = tuple(map(lambda v: float(v.text), vertex.xpath('*')))
                triangle_list = next(mesh.iter('polygonList'))
                for triangle in triangle_list:
                    # _print(tuple(map(lambda t: t.text, triangle.xpath('v'))))
                    vertex_ids = list(map(lambda p: int(p.text), triangle.xpath('v')))
                    if len(vertex_ids) == 3:
                        fv7_segment_meshes[int(segment.get("id"))][int(mesh.get("id"))]['triangles'][
                            int(triangle.get('PID'))] = tuple(vertex_ids), tuple()
                    elif len(vertex_ids) == 6:
                        fv7_segment_meshes[int(segment.get("id"))][int(mesh.get("id"))]['triangles'][
                            int(triangle.get('PID'))] = tuple(vertex_ids[::2]), tuple(vertex_ids[1::2])
                    else:
                        pass
        # _print(fv7_segment_meshes)
        fv8_segments = fv8.xpath('/segmentation/segment_list/segment')
        # extract vertices, normals and triangles
        fv8_segment_meshes = dict()
        for segment in fv8_segments:
            fv8_segment_meshes[int(segment.get("id"))] = dict()
            for mesh in segment.xpath('mesh_list/mesh'):
                fv8_segment_meshes[int(segment.get("id"))][int(mesh.get("id"))] = dict()
                vertices = next(mesh.iter('vertices'))
                # _print(vertices.keys())
                # _print(vertices.get("data").encode("ASCII"))
                vertex_list = _decode_data(vertices.get("data").encode('ASCII'),
                                           int(vertices.get("num_vertices")), vertices.get("mode"),
                                           vertices.get("endianness"))
                vertex_tuples = list(zip(vertex_list[::3], vertex_list[1::3], vertex_list[2::3]))
                # _print(data_vectors)
                fv8_segment_meshes[int(segment.get("id"))][int(mesh.get("id"))]['surface_vertices'] = dict(
                    zip(range(len(vertex_tuples)), vertex_tuples))
                # _print(data_dict)
                normals = next(mesh.iter('normals'))
                normal_list = _decode_data(normals.get("data").encode('ASCII'), int(normals.get("num_normals")),
                                           normals.get("mode"), normals.get('endianness'))
                normal_tuples = list(zip(normal_list[::3], normal_list[1::3], normal_list[2::3]))
                fv8_segment_meshes[int(segment.get("id"))][int(mesh.get("id"))]['normal_vertices'] = dict(
                    zip(range(len(normal_tuples)), normal_tuples))
                triangles = next(mesh.iter('triangles'))
                triangle_list = _decode_data(triangles.get("data").encode('ASCII'),
                                             int(triangles.get("num_triangles")),
                                             triangles.get("mode"), triangles.get('endianness'))
                triangle_tuples = list(zip(triangle_list[::3], triangle_list[1::3], triangle_list[2::3]))
                fv8_segment_meshes[int(segment.get("id"))][int(mesh.get("id"))]['triangles'] = dict(
                    zip(range(len(triangle_tuples)), triangle_tuples))
        # _print(fv8_segment_meshes)
        # compare
        fv7_surface_vertices = list()
        for segment_id in fv7_segment_meshes:
            for mesh_id in fv7_segment_meshes[segment_id]:
                for triangle_id in fv7_segment_meshes[segment_id][mesh_id]['triangles']:
                    triangle = fv7_segment_meshes[segment_id][mesh_id]['triangles'][triangle_id]
                    # _print(triangle)
                    # _print(triangle)
                    s0, s1, s2 = triangle[0]
                    # n0, n1, n2 = triangle[1]
                    fv7_surface_vertices += [fv7_segment_meshes[segment_id][mesh_id]['surface_vertices'][s0],
                                             fv7_segment_meshes[segment_id][mesh_id]['surface_vertices'][s1],
                                             fv7_segment_meshes[segment_id][mesh_id]['surface_vertices'][s2]]
        fv8_surface_vertices = list()
        for segment_id in fv8_segment_meshes:
            for mesh_id in fv8_segment_meshes[segment_id]:
                for triangle_id in fv8_segment_meshes[segment_id][mesh_id]['triangles']:
                    triangle = fv8_segment_meshes[segment_id][mesh_id]['triangles'][triangle_id]
                    # _print(triangle)
                    s0, s1, s2 = triangle
                    fv8_surface_vertices += [fv8_segment_meshes[segment_id][mesh_id]['surface_vertices'][s0],
                                             fv8_segment_meshes[segment_id][mesh_id]['surface_vertices'][s1],
                                             fv8_segment_meshes[segment_id][mesh_id]['surface_vertices'][s2]]
        # _print(fv7_surface_vertices[1283])
        # _print(fv8_surface_vertices[1283])
        self.assertEqual(len(fv7_surface_vertices), len(fv8_surface_vertices))
        for u, v in zip(fv7_surface_vertices, fv8_surface_vertices):
            self.assertAlmostEqual(u[0], v[0])
            self.assertAlmostEqual(u[1], v[1])
            self.assertAlmostEqual(u[2], v[2])

    def test_v0_7_0_dev0_to_v0_8_0_dev0_shapes(self):
        """Test that we can migrate shapes"""
        original = os.path.join(XML, 'test_shape_segmentation.sff')
        stylesheet = get_stylesheet("0.7.0.dev0", "0.8.0.dev1")
        _migrated = migrate_by_stylesheet(original, stylesheet)
        migrated = etree.ElementTree(etree.XML(_migrated))
        migrated_decoded = etree.tostring(migrated, xml_declaration=True, encoding='UTF-8', pretty_print=True).decode(
            'utf-8')
        sys.stderr.write(migrated_decoded)
        with open(os.path.join(XML, 'test_shape_segmentation_v0.8.0.dev1.sff'), 'w') as f:
            f.write(migrated_decoded)


class TestMain(unittest.TestCase):
    def test_parse_args(self):
        """Test parse_args function"""
        cmd = "file.xml -v"
        args = parse_args(cmd)
        self.assertEqual(args.infile, "file.xml")
        self.assertEqual(args.outfile, "file_v{}.xml".format(VERSION_LIST[-1]))

    def test_parse_args_outfile(self):
        """Test that outfile arg is honoured"""
        cmd = "file.xml -v -o nothing.xml"
        args = parse_args(cmd)
        self.assertEqual(args.outfile, "nothing.xml")

    def test_no_shlex(self):
        """Test not using shlex"""
        cmd = ["file.xml", "-v", "-o", "nothing.xml"]
        args = parse_args(cmd, use_shlex=False)
        self.assertEqual(args.infile, "file.xml")
        self.assertEqual(args.outfile, "nothing.xml")
