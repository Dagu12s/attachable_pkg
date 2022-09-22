import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

import attachable_pkg.mergeROSModels as merge


from launch_ros.actions import Node

import xacro

def generate_launch_description():

  use_sim_time = LaunchConfiguration('use_sim_time', default='false')
  pkg_ros_ign_gazebo = get_package_share_directory('ros_ign_gazebo')
  pkg_attach = get_package_share_directory('attachable_pkg')
  pkg_rm2 = get_package_share_directory('rm2_simulation')
  pkg_attach2 = "/home/david/rm2_workspace/src/attachable_pkg" # "~/rm2_workspace/src/attachable_pkg"
  
  
  
  # urdf_path = pkg_rm2 + '/models/rm2/rm2.urdf'
  # robot_desc = open(urdf_path).read()

  file_name = "actual_model"
  xacro_file_name = 'template.xacro'
  original_xacro_file = os.path.join(pkg_attach2, 'models','actual_model', xacro_file_name)
  xacro_file = os.path.join(pkg_attach2, 'models','actual_model', file_name + ".xacro")
  urdf_file = os.path.join(pkg_attach2, 'models','actual_model', file_name + ".urdf")
  
  with open(original_xacro_file) as fisrtfile, open(xacro_file ,"w") as secondfile:
    for line in fisrtfile:
      secondfile.write(line)
  
  robot_description_config = xacro.process_file(xacro_file, pretty_print=True)
  
  robot_desc = robot_description_config.toprettyxml()
  
  with open(urdf_file ,"w") as open_file:
      open_file.write(robot_desc)


  ign_gazebo = IncludeLaunchDescription( PythonLaunchDescriptionSource(
      os.path.join(pkg_ros_ign_gazebo, 'launch', 'ign_gazebo.launch.py'))
      ) 
  
  return LaunchDescription([
    DeclareLaunchArgument('ign_args',
        default_value=[os.path.join(pkg_attach, 'worlds', 'test_worldContactSensor2.sdf') +' --gui-config ' +
        os.path.join(pkg_attach, 'ign', 'gui.config'), ''], 
        description='Ignition Gazebo arguments'),
        ign_gazebo,
           #  spawn,
    Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time, 'robot_description': robot_desc}],
        arguments=[urdf_file]),
    Node(
        package='attachable_pkg',
        executable='rosActionServerMerger.py',
        name='AttachableJointActionServer',
        parameters=[{'urdf_update': True,
                     'urdf_file_name': pkg_attach2 +"/models/actual_model/actual_model"}],
        output='screen'
        ),


    Node(
        package='ros_ign_bridge',
        executable='parameter_bridge',
        arguments=['/AttacherContact/contact@std_msgs/msg/String@ignition.msgs.StringMsg'],
        output='screen'
        ),
    Node(
        package='ros_ign_bridge',
        executable='parameter_bridge',
        arguments=['/AttacherContact/touched@std_msgs/msg/Bool@ignition.msgs.Boolean'],
        output='screen'
        ),
    
    Node(
        package='ros_ign_bridge',
        executable='parameter_bridge',
        arguments=['/AttachableJoint@std_msgs/msg/String@ignition.msgs.StringMsg'],
        output='screen'
        ),

    Node(
        package='ros_ign_gazebo', executable='create',
        arguments=[
          '-name', 'rm2_1',
          '-file',  os.path.join(pkg_rm2, 'models', 'rm2', 'rm2_sim', 'model.sdf'),
          '-z', '0.18',
          '-y', '0',
          '-x', '1.25',
          ],
        output='screen',
          ),

    Node(
          package='ros_ign_gazebo', executable='create',
          arguments=[
            '-name', 'rm2_2',
            '-file',  os.path.join(pkg_rm2, 'models', 'rm2', 'rm2_sim', 'model.sdf'),
            '-z', '0.18',
            '-y', '0',
            '-x', '0.55',
            ],
          output='screen',
            )

    # Node(s
    #     package='ros_ign_bridge',
    #     executable='parameter_bridge',
    #     arguments=['/AttachableJoint@std_msgs/msg/String@ignition.msgs.StringMsg'],
    #     output='screen'
    #     ),
             
             
    # Node(
    #     package='ros_ign_gazebo', executable='create',
    #     arguments=[
    #       '-name', 'vehicle_1',
    #       '-file',  os.path.join(pkg_attach, 'models', 'vehicle', 'model.sdf'),
    #       '-z', '0',
    #       '-y', '0',
    #       '-x', '0',
    #       ],
    #     output='screen',
    #       ),

    # Node(
    #     package='ros_ign_gazebo', executable='create',
    #     arguments=[
    #       '-name', 'vehicle_2',
    #       '-file',  os.path.join(pkg_attach, 'models', 'vehicle', 'model.sdf'),
    #       '-z', '0',
    #       '-y', '0',
    #       '-x', '-2.5',
    #       ],
    #     output='screen',
    #       )
  
    # Node(
    #     package='ros_ign_gazebo', executable='create',
    #     arguments=[
    #       '-name', 'rm2_1',
    #       '-file',  os.path.join(pkg_rm2, 'models', 'rm2', 'rm2_sim', 'model.sdf'),
    #       '-z', '0',
    #       '-y', '0',
    #       '-x', '-2.5',
    #       ],
    #     output='screen',
    #       ),



      #     package='urdf_tutorial',
      #     executable='state_publisher',
      #     name='state_publisher',
      #     output='screen'),
    ])