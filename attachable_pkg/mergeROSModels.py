from dis import pretty_flags
import os
import sys
from unicodedata import name
from xml.dom.expatbuilder import Namespaces 
import xacro
from lxml import etree
from lxml.builder import E # lxml only !
from lxml.builder import ElementMaker # lxml only !
from xml.etree.ElementTree import ElementTree


def NAME(*args): # class is a reserved word in Python
     return {"name":' '.join(args)}
def TYPE(*args): # class is a reserved word in Python
     return {"type":' '.join(args)}



def addModel( filename, parentModel , parentLink, childModel, childLink):
    xacrons =  ElementMaker( namespace="http://wiki.ros.org/xacro")

    xacro_file = filename + ".xacro"
    urdf_file = filename + ".urdf"

    parentSplit = parentLink.split("_")
    childSplit = childModel.split("_")
    model = childSplit[0]
    # modelsufix = childSplit[3]

    jointName = "AttachableJoint_" + parentModel + "_" +  parentLink + "_" + childModel + "_" + childLink
    xacro_tree = etree.parse(xacro_file)
    robot = xacro_tree.getroot()
    

    robot.append(xacrons( model, sufix = childModel))
    robot.append(E.joint(NAME(jointName),TYPE("fixed"), E.parent(link=parentLink), E.child(link=childLink),
                 E.origin(rpy="0 0 0", xyz="0 0 0"))) 

    with open(xacro_file,"wb") as open_file:
        open_file.write(etree.tostring(xacro_tree, pretty_print=True))

    robot_description_config = xacro.process_file(xacro_file, pretty_print=True)
    robot_desc = robot_description_config.toprettyxml()

    with open(urdf_file ,"w") as open_file:
        open_file.write(robot_desc)


def removeModel( filename, parentModel , parentLink, childModel, childLink):
    xacrons =  ElementMaker( namespace="http://wiki.ros.org/xacro")

    xacro_file = filename + ".xacro"
    urdf_file = filename + ".urdf"
    
    childSplit = childModel.split("_")
    model = childSplit[0]

    jointName = "AttachableJoint_" + parentModel + "_" +  parentLink + "_" + childModel + "_" + childLink

    xacro_tree = etree.parse(xacro_file)
    robot = xacro_tree.getroot()

    jointList = robot.findall("joint")
    for joint in jointList:
        if joint.attrib["name"] == jointName:
            robot.remove(joint)
            
    modelList = robot.findall(".//xacro:" + model, namespaces = robot.nsmap)
    
    for element in modelList:
        if element.attrib["sufix"] == childModel:
            robot.remove(element)


    with open(xacro_file,"wb") as open_file:
        open_file.write(etree.tostring(xacro_tree, pretty_print=True))

    robot_description_config = xacro.process_file(xacro_file, pretty_print=True)
    robot_desc = robot_description_config.toprettyxml()

    with open(urdf_file ,"w") as open_file:
        open_file.write(robot_desc)



def createURDF(filename, modelList, modelNames, parentLinks, childLinks):    
    ROBOT = ElementMaker(nsmap={"xacro" : "http://wiki.ros.org/xacro"})
    xacrons =  ElementMaker( namespace="http://wiki.ros.org/xacro")

    xacro_file = filename + ".xacro"
    urdf_file = filename + ".urdf"



    xacro_tree = (ROBOT.robot(xacrons("include",filename="import_path.xacro")))

    # for model in modelList:
    #    xacro_tree.append(xacrons( model))
    for i in range(0,len(modelList)):
        xacro_tree.append(xacrons( modelList[i], sufix = modelNames[i]))
    
    for i in range(0,len(parentLinks)):
        jointName = "AttachableJoint_" + parentLinks[i] + "_" + childLinks[i]
        xacro_tree.append(E.joint(NAME(jointName),TYPE("fixed"), E.parent(link=parentLinks[i]), E.child(link=childLinks[i]),E.origin(rpy="0 0 0", xyz="0 0 0"))) 

    with open(xacro_file,"wb") as open_file:
        open_file.write(etree.tostring(xacro_tree, pretty_print=True))

    robot_description_config = xacro.process_file(xacro_file, pretty_print=True)
    robot_desc = robot_description_config.toprettyxml()

    with open(urdf_file ,"w") as open_file:
        open_file.write(robot_desc)


def createURDF2( filename, parentLinks, childLinks):
    ROBOT = ElementMaker(nsmap={"xacro" : "http://wiki.ros.org/xacro"})
    xacrons =  ElementMaker( namespace="http://wiki.ros.org/xacro")
    
    xacro_file = filename + ".xacro"
    urdf_file = filename + ".urdf"
    
    
    

    parentSplit = parentLinks[0].split("_")
    childSplit = childLinks[0].split("_")
    parentmodel = parentSplit[2]
    parentmodelsufix = parentSplit[3]
    childmodel = childSplit[2]
    childmodelsufix = childSplit[3]
    
    modelList = [parentmodel + parentmodelsufix]
    modelList.append(childmodel+childmodelsufix)

    jointName = "AttachableJoint_" + parentSplit[1]+parentSplit[2]+parentSplit[3] + "_" + childSplit[1]+childSplit[2]+childSplit[3]
    
    xacro_tree = (ROBOT.robot(xacrons("include",filename="import_path.xacro")))
    
    print("111")
    xacro_tree.append(xacrons( parentmodel, sufix = parentmodelsufix))
    xacro_tree.append(xacrons( childmodel, sufix = childmodelsufix))
    xacro_tree.append(E.joint(NAME(jointName),TYPE("fixed"), E.parent(link=parentLinks[0]), E.child(link=childLinks[0]),
                 E.origin(rpy="0 0 0", xyz="0 0 0"))) 

    
    for i in range(1,len(parentLinks)):
        print(i) 

        parentSplit = parentLinks[i].split("_")
        childSplit = childLinks[i].split("_")
        parentmodel = parentSplit[2]
        parentmodelsufix = parentSplit[3]
        childmodel = childSplit[2]
        childmodelsufix = childSplit[3]
        
        if (parentmodel+parentmodelsufix) not in modelList:
                xacro_tree.append(xacrons( parentmodel, sufix = parentmodelsufix))
                modelList.append(parentmodel+parentmodelsufix)
        
        if (childmodel+childmodelsufix) not in modelList:
                xacro_tree.append(xacrons( childmodel, sufix = childmodelsufix))
                modelList.append(childmodel+childmodelsufix)

        xacro_tree.append(E.joint(NAME(jointName),TYPE("fixed"), E.parent(link=parentLinks[i]), E.child(link=childLinks[i]),
                     E.origin(rpy="0 0 0", xyz="0 0 0"))) 


    with open(xacro_file,"wb") as open_file:
        open_file.write(etree.tostring(xacro_tree, pretty_print=True))

    robot_description_config = xacro.process_file(xacro_file, pretty_print=True)
    robot_desc = robot_description_config.toprettyxml()

    with open(urdf_file ,"w") as open_file:
        open_file.write(robot_desc)


def createURDF3( filename,parentModels, parentLinks,childModels, childLinks):
    ROBOT = ElementMaker(nsmap={"xacro" : "http://wiki.ros.org/xacro"})
    xacrons =  ElementMaker( namespace="http://wiki.ros.org/xacro")
    
    xacro_file = filename + ".xacro"
    urdf_file = filename + ".urdf"
    
    
    

    # parentSplit = parentLinks[0].split("_")
    # childSplit = childLinks[0].split("_")
    # parentmodel = parentSplit[2]
    # parentmodelsufix = parentSplit[3]
    # childmodel = childSplit[2]
    # childmodelsufix = childSplit[3]
    # jointName = "AttachableJoint_" + parentSplit[1]+parentSplit[2]+parentSplit[3] + "_" + childSplit[1]+childSplit[2]+childSplit[3]
    
    modelList = [parentModels[0]]
    modelList.append(childModels[0])


    jointName = "AttachableJoint_" + parentModels[0] + "_" +  parentLinks[0] + "_" + childModels[0] + "_" + childLinks[0]

    xacro_tree = (ROBOT.robot(xacrons("include",filename="import_path.xacro")))
    
    print("111")

    parentSplit = parentModels[0].split("_")
    parentmodel = parentSplit[0]
    
    childSplit = childModels[0].split("_")
    childmodel = childSplit[0]

    xacro_tree.append(xacrons( parentmodel, sufix = parentModels[0]))
    xacro_tree.append(xacrons( childmodel, sufix = childModels[0]))
    xacro_tree.append(E.joint(NAME(jointName),TYPE("fixed"), E.parent(link=parentLinks[0]), E.child(link=childLinks[0]),
                 E.origin(rpy="0 0 0", xyz="0 0 0"))) 

    
    for i in range(1,len(parentLinks)):
        print(i) 

        parentSplit = parentLinks[i].split("_")
        childSplit = childLinks[i].split("_")
        parentmodel = parentSplit[2]
        parentmodelsufix = parentSplit[3]
        childmodel = childSplit[2]
        childmodelsufix = childSplit[3]
        
        parentSplit = parentModels[i].split("_")
        parentmodel = parentSplit[i]
    
        childSplit = childModels[i].split("_")
        childmodel = childSplit[i]


        if (parentModels[i]) not in modelList:
                xacro_tree.append(xacrons( parentmodel, sufix = parentModels[i]))
                modelList.append(parentModels[i])
        
        if (childModels[i]) not in modelList:
                xacro_tree.append(xacrons( childmodel, sufix = childModels[i]))
                modelList.append(childModels[i])

        xacro_tree.append(E.joint(NAME(jointName),TYPE("fixed"), E.parent(link=parentLinks[i]), E.child(link=childLinks[i]),
                     E.origin(rpy="0 0 0", xyz="0 0 0"))) 


    with open(xacro_file,"wb") as open_file:
        open_file.write(etree.tostring(xacro_tree, pretty_print=True))

    robot_description_config = xacro.process_file(xacro_file, pretty_print=True)
    robot_desc = robot_description_config.toprettyxml()

    with open(urdf_file ,"w") as open_file:
        open_file.write(robot_desc)