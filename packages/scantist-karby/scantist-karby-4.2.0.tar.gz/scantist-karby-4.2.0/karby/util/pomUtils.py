# coding: utf-8
import os
import lxml.etree as ET



class ModifyXML(object):

    def __init__(self, file):
        self.origin_file = file  # 配置文件path
        self.tree = None
        self.EMPTY_TEXT = os.linesep
        self.XML_NS_NAME = ""
        self.XML_NS_VALUE = "http://maven.apache.org/POM/4.0.0"
        self.readXML()

    def readXML(self):
        self.tree = ET.parse(self.origin_file)
        # self.tree = ET.ElementTree()
        # ET.register_namespace(self.XML_NS_NAME, self.XML_NS_VALUE)
        # self.tree.parse(self.origin_file)

    def writeXML(self, out_path):
        self.tree.write(out_path, encoding="utf-8", xml_declaration=True)

    def addOWASPPlugin(self):
        """
        insert owasp plugin
        <plugin>
          <groupId>org.owasp</groupId>
          <artifactId>dependency-check-maven</artifactId>
          <version>6.4.1</version>
          <configuration>
            <format>JSON</format>
            <outputDirectory>.</outputDirectory>
            <assemblyAnalyzerEnabled>false</assemblyAnalyzerEnabled> 
            <nugetconfAnalyzerEnabled>false</nugetconfAnalyzerEnabled> 
            <nuspecAnalyzerEnabled>false</nuspecAnalyzerEnabled> 
          </configuration>
          <executions>
            <execution>
              <goals>
                <goal>aggregate</goal>
              </goals>
            </execution>
          </executions>
        </plugin>
        """
        root = self.tree.getroot()  # 根node
        for arts in root.iter(f"{{{self.XML_NS_VALUE}}}artifactId"):
            if arts.text == 'dependency-check-maven':
                print("dependency-check-maven already in pom")
                return
        if root.find(f"{{{self.XML_NS_VALUE}}}build") is None:
            new_build = ET.SubElement(root, f"{{{self.XML_NS_VALUE}}}build")
            new_build.text = self.EMPTY_TEXT
        for build in root.iter(f"{{{self.XML_NS_VALUE}}}build"):
            if build.find(f"{{{self.XML_NS_VALUE}}}plugins") is None:
                new_plugins = ET.SubElement(build, f"{{{self.XML_NS_VALUE}}}plugins")
                new_plugins.text = self.EMPTY_TEXT
            for plugins in build.getchildren():
                if plugins.tag == f"{{{self.XML_NS_VALUE}}}plugins":
                    new_plugin = ET.SubElement(plugins, f"{{{self.XML_NS_VALUE}}}plugin")
                    new_plugin.text = self.EMPTY_TEXT
                    new_groupId = ET.SubElement(new_plugin, f"{{{self.XML_NS_VALUE}}}groupId")
                    new_groupId.text = 'org.owasp'
                    new_artifactid = ET.SubElement(new_plugin, f"{{{self.XML_NS_VALUE}}}artifactId")
                    new_artifactid.text = 'dependency-check-maven'
                    new_version = ET.SubElement(new_plugin, f"{{{self.XML_NS_VALUE}}}version")
                    new_version.text = '6.4.1'
                    new_configuration = ET.SubElement(new_plugin, f"{{{self.XML_NS_VALUE}}}configuration")
                    new_configuration.text = self.EMPTY_TEXT
                    new_format = ET.SubElement(new_configuration, f"{{{self.XML_NS_VALUE}}}format")
                    new_format.text = 'JSON'
                    new_outputDirectory = ET.SubElement(new_configuration, f"{{{self.XML_NS_VALUE}}}outputDirectory")
                    new_outputDirectory.text = '.'
                    new_assemblyAnalyzerEnabled = ET.SubElement(new_configuration, f"{{{self.XML_NS_VALUE}}}assemblyAnalyzerEnabled")
                    new_assemblyAnalyzerEnabled.text = 'false'
                    new_nugetconfAnalyzerEnabled = ET.SubElement(new_configuration, f"{{{self.XML_NS_VALUE}}}nugetconfAnalyzerEnabled")
                    new_nugetconfAnalyzerEnabled.text = 'false'
                    new_nuspecAnalyzerEnabled = ET.SubElement(new_configuration, f"{{{self.XML_NS_VALUE}}}nuspecAnalyzerEnabled")
                    new_nuspecAnalyzerEnabled.text = 'false'
                    new_executions = ET.SubElement(new_plugin, f"{{{self.XML_NS_VALUE}}}executions")
                    new_executions.text = self.EMPTY_TEXT
                    new_execution = ET.SubElement(new_executions, f"{{{self.XML_NS_VALUE}}}execution")
                    new_execution.text = self.EMPTY_TEXT
                    new_goals = ET.SubElement(new_execution, f"{{{self.XML_NS_VALUE}}}goals")
                    new_goals.text = self.EMPTY_TEXT
                    new_goal = ET.SubElement(new_goals, f"{{{self.XML_NS_VALUE}}}goal")
                    new_goal.text = 'aggregate'

if __name__ == "__main__":
    origin_file = "/home/nryet/testProjects/SCAEvaluation/testsuit1/guava-23.0/guava-23.0/pom.xml"
    output = "/home/nryet/testProjects/SCAEvaluation/testsuit1/guava-23.0/guava-23.0/pom-new.xml"
    pom_xml = ModifyXML(origin_file)
    pom_xml.addOWASPPlugin()
    pom_xml.writeXML(output)
    print("修改pom.xml完成！")