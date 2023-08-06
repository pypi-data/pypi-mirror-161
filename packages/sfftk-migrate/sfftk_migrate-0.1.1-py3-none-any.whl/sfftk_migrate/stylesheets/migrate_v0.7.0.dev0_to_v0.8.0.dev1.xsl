<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

    <xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>

    <xsl:include href="identity.xsl"/>

    <!-- newline param -->
    <xsl:variable name="newline">
        <xsl:text>&#xa;</xsl:text>
    </xsl:variable>

    <!-- one-tab -->
    <xsl:variable name="tab-1">
        <xsl:text>&#009;</xsl:text>
    </xsl:variable>

    <!-- trow-tab -->
    <xsl:variable name="tab-2">
        <xsl:text>&#009;&#009;</xsl:text>
    </xsl:variable>

    <!-- three-tab -->
    <xsl:variable name="tab-3">
        <xsl:text>&#009;&#009;&#009;</xsl:text>
    </xsl:variable>

    <!-- four-tab -->
    <xsl:variable name="tab-4">
        <xsl:text>&#009;&#009;&#009;&#009;</xsl:text>
    </xsl:variable>

    <!-- five-tab -->
    <xsl:variable name="tab-5">
        <xsl:text>&#009;&#009;&#009;&#009;&#009;</xsl:text>
    </xsl:variable>

    <xsl:template match="/segmentation/version">
        <version>
            <xsl:text>0.8.0.dev1</xsl:text>
        </version>
    </xsl:template>

    <!-- primary descriptor -->
    <xsl:template match="/segmentation/primaryDescriptor">
        <primary_descriptor>
            <xsl:choose>
                <xsl:when test=".='threeDVolume'">
                    <xsl:text>three_d_volume</xsl:text>
                </xsl:when>
                <xsl:when test=".='meshList'">
                    <xsl:text>mesh_list</xsl:text>
                </xsl:when>
                <xsl:when test=".='shapePrimitiveList'">
                    <xsl:text>shape_primitive_list</xsl:text>
                </xsl:when>
            </xsl:choose>
        </primary_descriptor>
    </xsl:template>

    <!-- software -->
    <xsl:template match="/segmentation/software">
        <software_list>
            <xsl:copy-of select="$newline"/>
            <xsl:copy-of select="$tab-2"/>
            <software>
                <!-- when migrating software the existing software will always be index 0 -->
                <xsl:attribute name="id">0</xsl:attribute>
                <xsl:copy-of select="$newline"/>
                <xsl:copy-of select="$tab-3"/>
                <xsl:copy-of select="./name"/>
                <xsl:copy-of select="$newline"/>
                <xsl:copy-of select="$tab-3"/>
                <xsl:copy-of select="./version"/>
                <xsl:copy-of select="$newline"/>
                <xsl:copy-of select="$tab-3"/>
                <processing_details>
                    <xsl:value-of select="./processingDetails"/>
                </processing_details>
                <xsl:copy-of select="$newline"/>
                <xsl:copy-of select="$tab-2"/>
            </software>
            <xsl:copy-of select="$newline"/>
            <xsl:copy-of select="$tab-1"/>
        </software_list>
    </xsl:template>

    <!-- bounding box -->
    <xsl:template match="/segmentation/boundingBox">
        <bounding_box>
            <xsl:copy-of select="@xmin"/>
            <xsl:copy-of select="@xmax"/>
            <xsl:copy-of select="@ymin"/>
            <xsl:copy-of select="@ymax"/>
            <xsl:copy-of select="@zmin"/>
            <xsl:copy-of select="@zmax"/>
        </bounding_box>
    </xsl:template>

    <!-- transform list -->
    <xsl:template match="/segmentation/transformList">
        <transform_list>
            <xsl:for-each select="transformationMatrix">
                <xsl:copy-of select="$newline"/>
                <xsl:copy-of select="$tab-2"/>
                <transformation_matrix>
                    <xsl:attribute name="id">
                        <xsl:value-of select="@id"/>
                    </xsl:attribute>
                    <xsl:copy-of select="$newline"/>
                    <xsl:copy-of select="$tab-3"/>
                    <xsl:copy-of select="rows"/>
                    <xsl:copy-of select="$newline"/>
                    <xsl:copy-of select="$tab-3"/>
                    <xsl:copy-of select="cols"/>
                    <xsl:copy-of select="$newline"/>
                    <xsl:copy-of select="$tab-3"/>
                    <xsl:copy-of select="data"/>
                    <xsl:copy-of select="$newline"/>
                    <xsl:copy-of select="$tab-2"/>
                </transformation_matrix>
            </xsl:for-each>
            <xsl:copy-of select="$newline"/>
            <xsl:copy-of select="$tab-1"/>
        </transform_list>
    </xsl:template>

    <!-- global external references -->
    <xsl:template match="/segmentation/globalExternalReferences">
        <global_external_references>
            <xsl:for-each select="./ref">
                <xsl:copy-of select="$newline"/>
                <xsl:copy-of select="$tab-2"/>
                <ref>
                    <xsl:choose>
                        <xsl:when test="@id">
                            <xsl:attribute name="id">
                                <xsl:value-of select="@id"/>
                            </xsl:attribute>
                        </xsl:when>
                    </xsl:choose>
                    <xsl:attribute name="resource">
                        <xsl:value-of select="@type"/>
                    </xsl:attribute>
                    <xsl:attribute name="url">
                        <xsl:value-of select="@otherType"/>
                    </xsl:attribute>
                    <xsl:attribute name="accession">
                        <xsl:value-of select="@value"/>
                    </xsl:attribute>
                    <xsl:copy-of select="@label"/>
                    <xsl:copy-of select="@description"/>
                </ref>
            </xsl:for-each>
            <xsl:copy-of select="$newline"/>
            <xsl:copy-of select="$tab-1"/>
        </global_external_references>
    </xsl:template>

    <!-- mesh components -->
    <xsl:template match="/segmentation/segmentList/segment">
        <xsl:for-each select=".">
            <xsl:variable name="segment" select="position()"/>
            <xsl:message terminate="yes">
                Something to report
            </xsl:message>
        </xsl:for-each>
    </xsl:template>

    <!-- segments -->
    <xsl:template match="/segmentation/segmentList">
        <segment_list>
            <xsl:for-each select="./segment">
                <xsl:copy-of select="$newline"/>
                <xsl:copy-of select="$tab-2"/>
                <segment>
                    <xsl:copy-of select="@id"/>
                    <xsl:attribute name="parent_id">
                        <xsl:value-of select="@parentID"/>
                    </xsl:attribute>
                    <xsl:copy-of select="$newline"/>
                    <xsl:copy-of select="$tab-3"/>
                    <biological_annotation>
                        <xsl:if test="count(./biologicalAnnotation/name) = 1">
                            <xsl:copy-of select="$newline"/>
                            <xsl:copy-of select="$tab-4"/>
                            <xsl:copy-of select="./biologicalAnnotation/name"/>
                            <xsl:copy-of select="$newline"/>
                            <xsl:copy-of select="$tab-4"/>
                        </xsl:if>
                        <xsl:if test="count(./biologicalAnnotation/description) = 1">
                            <xsl:copy-of select="$newline"/>
                            <xsl:copy-of select="$tab-4"/>
                            <xsl:copy-of select="./biologicalAnnotation/description"/>
                            <xsl:copy-of select="$newline"/>
                            <xsl:copy-of select="$tab-4"/>
                        </xsl:if>
                        <xsl:if test="count(./biologicalAnnotation/externalReferences/ref) > 0">
                            <external_references>
                                <xsl:for-each select="./biologicalAnnotation/externalReferences/ref">
                                    <xsl:copy-of select="$newline"/>
                                    <xsl:copy-of select="$tab-5"/>
                                    <ref>
                                        <xsl:match select="@id">
                                            <xsl:attribute name="id">
                                                <xsl:value-of select="@id"/>
                                            </xsl:attribute>
                                        </xsl:match>
                                        <xsl:attribute name="resource">
                                            <xsl:value-of select="@type"/>
                                        </xsl:attribute>
                                        <xsl:attribute name="url">
                                            <xsl:value-of select="@otherType"/>
                                        </xsl:attribute>
                                        <xsl:attribute name="accession">
                                            <xsl:value-of select="@value"/>
                                        </xsl:attribute>
                                        <xsl:copy-of select="@label"/>
                                        <xsl:copy-of select="@description"/>
                                    </ref>
                                    <xsl:copy-of select="$newline"/>
                                    <xsl:copy-of select="$tab-4"/>
                                </xsl:for-each>
                            </external_references>
                            <!--                            <xsl:copy-of select="$newline"/>-->
                            <!--                            <xsl:copy-of select="$tab-3"/>-->
                        </xsl:if>
                    </biological_annotation>
                    <xsl:copy-of select="$newline"/>
                    <xsl:copy-of select="$tab-3"/>
                    <xsl:copy-of select="./colour"/>
                    <xsl:copy-of select="$newline"/>
                    <xsl:copy-of select="$tab-3"/>
                    <xsl:if test="./threeDVolume">
                            <three_d_volume>
                                <xsl:copy-of select="$newline"/>
                                <xsl:copy-of select="$tab-4"/>
                                <lattice_id>
                                    <xsl:value-of select="./threeDVolume/latticeId"/>
                                </lattice_id>
                                <xsl:copy-of select="$newline"/>
                                <xsl:copy-of select="$tab-4"/>
                                <xsl:copy-of select="./threeDVolume/value"/>
                                <xsl:copy-of select="$newline"/>
                                <xsl:choose>
                                    <xsl:when test="./threeDVolume/transformId">
                                        <xsl:copy-of select="$tab-4"/>
                                        <transform_id>
                                            <xsl:value-of select="./threeDVolume/transformId"/>
                                        </transform_id>
                                        <xsl:copy-of select="$newline"/>
                                    </xsl:when>
                                </xsl:choose>
                                <xsl:copy-of select="$tab-3"/>
                            </three_d_volume>
                        </xsl:if>
                    <xsl:if test="./meshList">
                            <mesh_list>
                                <xsl:for-each select="./meshList/mesh">
                                    <xsl:copy-of select="$newline"/>
                                    <xsl:copy-of select="$tab-4"/>
                                    <mesh>
                                        <xsl:copy-of select="@id"/>
                                        <!--                                        <xsl:copy-of select="$newline"/>-->
                                        <!--                                        <xsl:copy-of select="$tab-5"/>-->
                                        <xsl:choose>
                                            <xsl:when test="./transformId">
                                                <xsl:copy-of select="$newline"/>
                                                <xsl:copy-of select="$tab-5"/>
                                                <transform_id>
                                                    <xsl:value-of select="./transformId"/>
                                                </transform_id>
                                                <xsl:copy-of select="$newline"/>
                                                <xsl:copy-of select="$tab-4"/>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <xsl:copy-of select="$newline"/>
                                                <xsl:copy-of select="$tab-5"/>
                                            </xsl:otherwise>
                                        </xsl:choose>
                                    </mesh>
                                </xsl:for-each>
                                <xsl:copy-of select="$newline"/>
                                <xsl:copy-of select="$tab-3"/>
                            </mesh_list>
                        </xsl:if>
                    <xsl:if test="./shapePrimitiveList">
                            <shape_primitive_list>
                                <xsl:for-each select="./shapePrimitiveList/child::node()">
                                    <xsl:choose>
                                        <xsl:when test="name() = 'cone'">
                                            <xsl:copy-of select="$newline"/>
                                            <xsl:copy-of select="$tab-4"/>
                                            <cone>
                                                <xsl:attribute name="id">
                                                    <xsl:value-of select="./@id"/>
                                                </xsl:attribute>
                                                <xsl:copy-of select="$newline"/>
                                                <xsl:copy-of select="$tab-5"/>
                                                <xsl:copy-of select="./height"/>
                                                <xsl:copy-of select="$newline"/>
                                                <xsl:copy-of select="$tab-5"/>
                                                <bottom_radius>
                                                    <xsl:value-of select="./bottomRadius"/>
                                                </bottom_radius>
                                                <xsl:copy-of select="$newline"/>
                                                <xsl:copy-of select="$tab-5"/>
                                                <transform_id>
                                                    <xsl:value-of select="./transformId"/>
                                                </transform_id>
                                                <xsl:copy-of select="$newline"/>
                                                <xsl:copy-of select="$tab-4"/>
                                            </cone>
                                        </xsl:when>
                                        <xsl:when test="name() = 'cuboid'">
                                            <xsl:copy-of select="$newline"/>
                                            <xsl:copy-of select="$tab-4"/>
                                            <cuboid>
                                                <xsl:attribute name="id">
                                                    <xsl:value-of select="./@id"/>
                                                </xsl:attribute>
                                                <xsl:copy-of select="$newline"/>
                                                <xsl:copy-of select="$tab-5"/>
                                                <xsl:copy-of select="./x"/>
                                                <xsl:copy-of select="$newline"/>
                                                <xsl:copy-of select="$tab-5"/>
                                                <xsl:copy-of select="./y"/>
                                                <xsl:copy-of select="$newline"/>
                                                <xsl:copy-of select="$tab-5"/>
                                                <xsl:copy-of select="./z"/>
                                                <xsl:copy-of select="$newline"/>
                                                <xsl:copy-of select="$tab-5"/>
                                                <transform_id>
                                                    <xsl:value-of select="./transformId"/>
                                                </transform_id>
                                                <xsl:copy-of select="$newline"/>
                                                <xsl:copy-of select="$tab-4"/>
                                            </cuboid>
                                        </xsl:when>
                                        <xsl:when test="name() = 'cylinder'">
                                            <xsl:copy-of select="$newline"/>
                                            <xsl:copy-of select="$tab-4"/>
                                            <cylinder>
                                                <xsl:attribute name="id">
                                                    <xsl:value-of select="./@id"/>
                                                </xsl:attribute>
                                                <xsl:copy-of select="$newline"/>
                                                <xsl:copy-of select="$tab-5"/>
                                                <xsl:copy-of select="./height"/>
                                                <xsl:copy-of select="$newline"/>
                                                <xsl:copy-of select="$tab-5"/>
                                                <xsl:copy-of select="./diameter"/>
                                                <xsl:copy-of select="$newline"/>
                                                <xsl:copy-of select="$tab-5"/>
                                                <transform_id>
                                                    <xsl:value-of select="./transformId"/>
                                                </transform_id>
                                                <xsl:copy-of select="$newline"/>
                                                <xsl:copy-of select="$tab-4"/>
                                            </cylinder>
                                        </xsl:when>
                                        <xsl:when test="name() = 'ellipsoid'">
                                            <xsl:copy-of select="$newline"/>
                                            <xsl:copy-of select="$tab-4"/>
                                            <ellipsoid>
                                                <xsl:attribute name="id">
                                                    <xsl:value-of select="./@id"/>
                                                </xsl:attribute>
                                                <xsl:copy-of select="$newline"/>
                                                <xsl:copy-of select="$tab-5"/>
                                                <xsl:copy-of select="./x"/>
                                                <xsl:copy-of select="$newline"/>
                                                <xsl:copy-of select="$tab-5"/>
                                                <xsl:copy-of select="./y"/>
                                                <xsl:copy-of select="$newline"/>
                                                <xsl:copy-of select="$tab-5"/>
                                                <xsl:copy-of select="./z"/>
                                                <xsl:copy-of select="$newline"/>
                                                <xsl:copy-of select="$tab-5"/>
                                                <transform_id>
                                                    <xsl:value-of select="./transformId"/>
                                                </transform_id>
                                                <xsl:copy-of select="$newline"/>
                                                <xsl:copy-of select="$tab-4"/>
                                            </ellipsoid>
                                        </xsl:when>
                                    </xsl:choose>
                                </xsl:for-each>
                                <xsl:copy-of select="$newline"/>
                                <xsl:copy-of select="$tab-3"/>
                            </shape_primitive_list>
                        </xsl:if>
<!--                    <xsl:choose>-->
<!--                        <xsl:when test="./threeDVolume">-->
<!--                            <three_d_volume>-->
<!--                                <xsl:copy-of select="$newline"/>-->
<!--                                <xsl:copy-of select="$tab-4"/>-->
<!--                                <lattice_id>-->
<!--                                    <xsl:value-of select="./threeDVolume/latticeId"/>-->
<!--                                </lattice_id>-->
<!--                                <xsl:copy-of select="$newline"/>-->
<!--                                <xsl:copy-of select="$tab-4"/>-->
<!--                                <xsl:copy-of select="./threeDVolume/value"/>-->
<!--                                <xsl:copy-of select="$newline"/>-->
<!--                                <xsl:choose>-->
<!--                                    <xsl:when test="./threeDVolume/transformId">-->
<!--                                        <xsl:copy-of select="$tab-4"/>-->
<!--                                        <transform_id>-->
<!--                                            <xsl:value-of select="./threeDVolume/transformId"/>-->
<!--                                        </transform_id>-->
<!--                                        <xsl:copy-of select="$newline"/>-->
<!--                                    </xsl:when>-->
<!--                                </xsl:choose>-->
<!--                                <xsl:copy-of select="$tab-3"/>-->
<!--                            </three_d_volume>-->
<!--                        </xsl:when>-->
<!--                        <xsl:when test="./meshList">-->
<!--                            <mesh_list>-->
<!--                                <xsl:for-each select="./meshList/mesh">-->
<!--                                    <xsl:copy-of select="$newline"/>-->
<!--                                    <xsl:copy-of select="$tab-4"/>-->
<!--                                    <mesh>-->
<!--                                        <xsl:copy-of select="@id"/>-->
<!--                                        &lt;!&ndash;                                        <xsl:copy-of select="$newline"/>&ndash;&gt;-->
<!--                                        &lt;!&ndash;                                        <xsl:copy-of select="$tab-5"/>&ndash;&gt;-->
<!--                                        <xsl:choose>-->
<!--                                            <xsl:when test="./transformId">-->
<!--                                                <xsl:copy-of select="$newline"/>-->
<!--                                                <xsl:copy-of select="$tab-5"/>-->
<!--                                                <transform_id>-->
<!--                                                    <xsl:value-of select="./transformId"/>-->
<!--                                                </transform_id>-->
<!--                                                <xsl:copy-of select="$newline"/>-->
<!--                                                <xsl:copy-of select="$tab-4"/>-->
<!--                                            </xsl:when>-->
<!--                                            <xsl:otherwise>-->
<!--                                                <xsl:copy-of select="$newline"/>-->
<!--                                                <xsl:copy-of select="$tab-5"/>-->
<!--                                            </xsl:otherwise>-->
<!--                                        </xsl:choose>-->
<!--                                    </mesh>-->
<!--                                </xsl:for-each>-->
<!--                                <xsl:copy-of select="$newline"/>-->
<!--                                <xsl:copy-of select="$tab-3"/>-->
<!--                            </mesh_list>-->
<!--                        </xsl:when>-->
<!--                        <xsl:when test="./shapePrimitiveList">-->
<!--                            <shape_primitive_list>-->
<!--                                <xsl:for-each select="./shapePrimitiveList/child::node()">-->
<!--                                    <xsl:choose>-->
<!--                                        <xsl:when test="name() = 'cone'">-->
<!--                                            <xsl:copy-of select="$newline"/>-->
<!--                                            <xsl:copy-of select="$tab-4"/>-->
<!--                                            <cone>-->
<!--                                                <xsl:attribute name="id">-->
<!--                                                    <xsl:value-of select="./@id"/>-->
<!--                                                </xsl:attribute>-->
<!--                                                <xsl:copy-of select="$newline"/>-->
<!--                                                <xsl:copy-of select="$tab-5"/>-->
<!--                                                <xsl:copy-of select="./height"/>-->
<!--                                                <xsl:copy-of select="$newline"/>-->
<!--                                                <xsl:copy-of select="$tab-5"/>-->
<!--                                                <bottom_radius>-->
<!--                                                    <xsl:value-of select="./bottomRadius"/>-->
<!--                                                </bottom_radius>-->
<!--                                                <xsl:copy-of select="$newline"/>-->
<!--                                                <xsl:copy-of select="$tab-5"/>-->
<!--                                                <transform_id>-->
<!--                                                    <xsl:value-of select="./transformId"/>-->
<!--                                                </transform_id>-->
<!--                                                <xsl:copy-of select="$newline"/>-->
<!--                                                <xsl:copy-of select="$tab-4"/>-->
<!--                                            </cone>-->
<!--                                        </xsl:when>-->
<!--                                        <xsl:when test="name() = 'cuboid'">-->
<!--                                            <xsl:copy-of select="$newline"/>-->
<!--                                            <xsl:copy-of select="$tab-4"/>-->
<!--                                            <cuboid>-->
<!--                                                <xsl:attribute name="id">-->
<!--                                                    <xsl:value-of select="./@id"/>-->
<!--                                                </xsl:attribute>-->
<!--                                                <xsl:copy-of select="$newline"/>-->
<!--                                                <xsl:copy-of select="$tab-5"/>-->
<!--                                                <xsl:copy-of select="./x"/>-->
<!--                                                <xsl:copy-of select="$newline"/>-->
<!--                                                <xsl:copy-of select="$tab-5"/>-->
<!--                                                <xsl:copy-of select="./y"/>-->
<!--                                                <xsl:copy-of select="$newline"/>-->
<!--                                                <xsl:copy-of select="$tab-5"/>-->
<!--                                                <xsl:copy-of select="./z"/>-->
<!--                                                <xsl:copy-of select="$newline"/>-->
<!--                                                <xsl:copy-of select="$tab-5"/>-->
<!--                                                <transform_id>-->
<!--                                                    <xsl:value-of select="./transformId"/>-->
<!--                                                </transform_id>-->
<!--                                                <xsl:copy-of select="$newline"/>-->
<!--                                                <xsl:copy-of select="$tab-4"/>-->
<!--                                            </cuboid>-->
<!--                                        </xsl:when>-->
<!--                                        <xsl:when test="name() = 'cylinder'">-->
<!--                                            <xsl:copy-of select="$newline"/>-->
<!--                                            <xsl:copy-of select="$tab-4"/>-->
<!--                                            <cylinder>-->
<!--                                                <xsl:attribute name="id">-->
<!--                                                    <xsl:value-of select="./@id"/>-->
<!--                                                </xsl:attribute>-->
<!--                                                <xsl:copy-of select="$newline"/>-->
<!--                                                <xsl:copy-of select="$tab-5"/>-->
<!--                                                <xsl:copy-of select="./height"/>-->
<!--                                                <xsl:copy-of select="$newline"/>-->
<!--                                                <xsl:copy-of select="$tab-5"/>-->
<!--                                                <xsl:copy-of select="./diameter"/>-->
<!--                                                <xsl:copy-of select="$newline"/>-->
<!--                                                <xsl:copy-of select="$tab-5"/>-->
<!--                                                <transform_id>-->
<!--                                                    <xsl:value-of select="./transformId"/>-->
<!--                                                </transform_id>-->
<!--                                                <xsl:copy-of select="$newline"/>-->
<!--                                                <xsl:copy-of select="$tab-4"/>-->
<!--                                            </cylinder>-->
<!--                                        </xsl:when>-->
<!--                                        <xsl:when test="name() = 'ellipsoid'">-->
<!--                                            <xsl:copy-of select="$newline"/>-->
<!--                                            <xsl:copy-of select="$tab-4"/>-->
<!--                                            <ellipsoid>-->
<!--                                                <xsl:attribute name="id">-->
<!--                                                    <xsl:value-of select="./@id"/>-->
<!--                                                </xsl:attribute>-->
<!--                                                <xsl:copy-of select="$newline"/>-->
<!--                                                <xsl:copy-of select="$tab-5"/>-->
<!--                                                <xsl:copy-of select="./x"/>-->
<!--                                                <xsl:copy-of select="$newline"/>-->
<!--                                                <xsl:copy-of select="$tab-5"/>-->
<!--                                                <xsl:copy-of select="./y"/>-->
<!--                                                <xsl:copy-of select="$newline"/>-->
<!--                                                <xsl:copy-of select="$tab-5"/>-->
<!--                                                <xsl:copy-of select="./z"/>-->
<!--                                                <xsl:copy-of select="$newline"/>-->
<!--                                                <xsl:copy-of select="$tab-5"/>-->
<!--                                                <transform_id>-->
<!--                                                    <xsl:value-of select="./transformId"/>-->
<!--                                                </transform_id>-->
<!--                                                <xsl:copy-of select="$newline"/>-->
<!--                                                <xsl:copy-of select="$tab-4"/>-->
<!--                                            </ellipsoid>-->
<!--                                        </xsl:when>-->
<!--                                    </xsl:choose>-->
<!--                                </xsl:for-each>-->
<!--                                <xsl:copy-of select="$newline"/>-->
<!--                                <xsl:copy-of select="$tab-3"/>-->
<!--                            </shape_primitive_list>-->
<!--                        </xsl:when>-->
<!--                    </xsl:choose>-->
                    <xsl:copy-of select="$newline"/>
                    <xsl:copy-of select="$tab-2"/>
                </segment>
            </xsl:for-each>
            <xsl:copy-of select="$newline"/>
            <xsl:copy-of select="$tab-1"/>
        </segment_list>
    </xsl:template>

    <!-- lattice list -->
    <xsl:template match="/segmentation/latticeList">
        <lattice_list>
            <xsl:for-each select="./lattice">
                <xsl:copy-of select="$newline"/>
                <xsl:copy-of select="$tab-2"/>
                <xsl:copy-of select="."/>
            </xsl:for-each>
            <xsl:copy-of select="$newline"/>
            <xsl:copy-of select="$tab-1"/>
        </lattice_list>
    </xsl:template>

</xsl:stylesheet>
