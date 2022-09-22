#!/usr/bin/env python3
from mimetypes import init
from re import S
import time
from urllib import request

from numpy import empty

import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node

from attachable_pkg.action import AttachModel
from std_msgs.msg import String
from std_msgs.msg import Int32
from std_msgs.msg import Empty
from std_msgs.msg import Bool
import attachable_pkg.mergeROSModels as merge

from rcl_interfaces.srv import SetParameters
from rcl_interfaces.msg import Parameter
from rcl_interfaces.msg import ParameterValue

class AttachableJointActionServer(Node):

    def __init__(self):
        self.contact = False
        super().__init__('AttachableJointActionServer')
        self._action_server = ActionServer(
            self,
            AttachModel,
            'AttachableJoint',
            self.execute_callback)
        self.robotStatePublisherClient = self.create_client(SetParameters, '/robot_state_publisher/set_parameters')
        self.contactPublisherTopic = "/AttacherContact/contact"
        self.contactSubscriberTopic = "/AttacherContact/touched"
        self.contactPublisher = self.create_publisher(String, self.contactPublisherTopic,10)
        self.contactSubscriber = self.create_subscription(Bool, self.contactSubscriberTopic, self.contactSubscriber_callack, 10)
        
        self.attachableJointErrorSubscriber = self.create_subscription(Int32, self.contactSubscriberTopic, self.errorSubscriber_callack, 10)

        self.attachableJointPublisher = self.create_publisher(String, "/AttachableJoint" ,10)

        self.msgToPublish = String()

        self.error = 0

        self.declare_parameter('urdf_update', False)
        self.urdf_update = self.get_parameter('urdf_update').get_parameter_value().bool_value

        self.declare_parameter('urdf_file_name', "actual_model")
        self.filename = self.get_parameter('urdf_file_name').get_parameter_value().string_value

            

    def contactSubscriber_callack(self, msg):
        self.contact = msg.data        


    def errorSubscriber_callack(self, msg):
        self.error = msg.data        



    def waitToResponse(self, timeout):
        initTime = time.time()
        while rclpy.ok():
            rclpy.spin_once(self)
            if ((time.time() - initTime) > timeout):
                break


    def attachModelIgnition(self, request):
        
        self.msgToPublish.data = '[{}][{}][{}][{}][{}]'.format(self.parentModel, self.parentLink, self.childModel, self.childLink, request)
        self.attachableJointPublisher.publish(self.msgToPublish)


    def restartStatePublisher(self):
        self.get_logger().info('Restart State Publisher...')
        
        req = SetParameters.Request()

        parametervalue = ParameterValue()
        parameter = Parameter()

        parametervalue.type=4
        parametervalue.bool_value=False
        parametervalue.integer_value=0
        parametervalue.double_value=0.0
        
        parametervalue.byte_array_value=[]
        parametervalue.bool_array_value=[]
        parametervalue.integer_array_value=[]
        parametervalue.double_array_value=[]
        parametervalue.string_array_value=[]

        file = open(self.filename+".urdf")
        parametervalue.string_value = file.read()
        file.close()

        parameter.name = 'robot_description'
        parameter.value = parametervalue

        req.parameters = [parameter]

        future = self.robotStatePublisherClient.call_async(req)

        # robot_description_config = xacro.process_file(self.filename)
        # robot_desc = robot_description_config.toxml()
  
        
    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')
        
        result = AttachModel.Result()

        feedback_msg = AttachModel.Feedback()
        self.childLink = goal_handle.request.child_link
        self.parentLink = goal_handle.request.parent_link
        self.childModel = goal_handle.request.child_model
        self.parentModel = goal_handle.request.parent_model

        self.get_logger().info("Executing Goal...")
        if True == goal_handle.request.attach:
            #Check if the linsk are touching       
            self.msgToPublish.data = '[{}][{}][{}][{}]'.format(self.parentModel, self.parentLink, self.childModel, self.childLink)

            self.contactPublisher.publish(self.msgToPublish)
            
            self.waitToResponse(0.5)

            self.msgToPublish.data = 'end'
            self.contactPublisher.publish(self.msgToPublish)

            if self.contact:

                self.get_logger().info("Links are in contact, Attaching models...")

                #Add model in Gazebo Ingition
                self.attachModelIgnition("attach")

                # self.waitToResponse(0.5)

                feedback_msg = self.error
                if (self.error == 0) and (self.urdf_update == True):
                    print(1)
                    #Add model in URDF
                    merge.addModel(self.filename, "body_1", "AttachableLink_1_body_1", "leg_1", "AttachableLink_1_leg_1") #"AttachableLink_1_body_1", "AttachableLink_1_leg_1" )#
                    print(2)
                    #Restart State Publisher with the new URDF
                    self.restartStatePublisher()

                    result.response = "True"
            else:
                self.get_logger().info("Links are NOT in contact. End.")
                result.response = "False"

        else:
            #Detach Models in ignition
            self.get_logger().info("Detach models...")

            self.attachModelIgnition("detach")

            # self.waitToResponse(0.5)
        
            feedback_msg = self.error
            if (self.error == 0) and (self.urdf_update == True) :
                #Remove model in URDF

                merge.removeModel(self.filename, "body_1", "AttachableLink_1_body_1", "leg_1", "AttachableLink_1_leg_1") #"AttachableLink_1_body_1", "AttachableLink_1_leg_1" )#

                #Reset robot state publisher
                self.restartStatePublisher()

                result.response = "True"

        result.response = "Contact Done: " + result.response + " || Error: " + str(self.error)
        goal_handle.succeed()        

        return result



def main(args=None):
    rclpy.init(args=args)


    attachable_joint_action_server = AttachableJointActionServer()
    
    while rclpy.ok():
        rclpy.spin_once(attachable_joint_action_server)
    

if __name__ == '__main__':
    main()

