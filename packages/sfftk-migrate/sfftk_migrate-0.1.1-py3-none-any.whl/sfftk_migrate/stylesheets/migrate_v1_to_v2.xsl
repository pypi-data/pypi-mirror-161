<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>

    <!--params-->
    <xsl:param name="segmentation_details"/>

    <xsl:include href="identity.xsl"/>

    <xsl:template match="/segmentation/version">
        <version>
            <xsl:text>2</xsl:text>
        </version>
    </xsl:template>

    <xsl:template match="segment">
        <xsl:copy-of select="."/>
        <xsl:text>&#xa;</xsl:text> <!--newline-->
        <details>
            <xsl:value-of select="$segmentation_details"/>
        </details>
    </xsl:template>

</xsl:stylesheet>
