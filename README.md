# attachable_pkg

# 1. AttachableJoint
Para iniciar el Attach hay que meter en el .sdf del world:

```jsx
<plugin filename="/home/david/workspace/src/ign-gazebo/examples/plugin/system_plugin/build/libAttachableJoint.so" name="attachable_joint::AttachableJoint">
</plugin>
```

Para activarlo en la simulación hay que enviar un mensaje al topic `/AttachableJoint` con la siguiente estructura:

```jsx
[parentModel][parentLink][childModel][childLink][attach_request]
```

La `attach_request` puede ser o `attach` para unir 2 links o `detach` para separarlos

```jsx
ign topic -t /AttachableJoint -m ignition.msgs.StringMsg -p 'data: "[rm2_1][AttachableLink_1_rm2_1][rm2_2][AttachableLink_1_rm2_1][attach]" '

	ign topic -t /AttachableJoint -m ignition.msgs.StringMsg -p 'data: "[box0][box_body][box2][box_body][attach]" '
ign topic -t /AttachableJoint -m ignition.msgs.StringMsg -p 'data: "[vehicle_blue][AttachableLink_1_vehicle_1][box0][box_body][attach]" '

```

Si hay un modelo que se ha incluido en el SDF de este modo:

Es un modelo al que llamas en el sdf mod1 pero que se llama b

```jsx
<model name="mod1">
	<include>
		<pose>0 0 0.45 0 0 0</pose> <!-- Z for mine-->
	  <uri>model://rm2_body</uri>
	  <name>b</name>
  </include>
</model>
```

En ese caso hay que referirse a link [b::bodylink]

```jsx
ign topic -t /AttachableJoint -m ignition.msgs.StringMsg -p 'data:"[mod1][b::bodyLink][box2][box_body][attach]'
```

Se ha implementado un topic de gestión de errores: `/AttachableJoint/error` El cual es del tipo int32. El código de error es el siguiente:
| 0 | No hay error |
| --- | --- |
| 1 | No se han encontrado Link especificado |
| 2 | Ya se ha creado ese joint |

# 2.  AttacherContact

Comprueba si 2 links se están tocando, envías un mensaje de tipo al topic: `/AttacherContact/contact` del tipo: `[modelo_link1][link1][modelo_link2][link2]`

y te responde true o false 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en el topic `/AttacheContact/touched` 

```jsx
ign topic -t /AttacherContact/contact -m ignition.msgs.StringMsg -p 'data:"[rm2_1][AttachableLink_1_rm2_1][rm2_2][AttachableLink_1_rm2_1]"'
ign topic -t /AttacherContact/contact -m ignition.msgs.StringMsg -p 'data:"[vehicle_blue][AttachableLink_1_vehicle_1][wall_1][AttachableLink_1_wall_1]"'
ign topic -t /AttacherContact/contact -m ignition.msgs.StringMsg -p 'data:"[vehicle_blue][AttachableLink_1_vehicle_1][box0][box_body]"'

ign topic -t /AttacherContact/contact -m ignition.msgs.StringMsg -p 'data:"[rm2_1][AttachableLink_1_rm2_1][wall_1][AttachableLink_1_wall_1]"'
```

Para parar el plugin:

```jsx
ign topic -t /AttacherContact/contact -m ignition.msgs.StringMsg -p 'data:"end"'
```

Para ver si se están tocando:

```jsx
ign topic -e -t /AttacherContact/touched
```
# Action server

Action server es un paquete de ros que gestiona varias cosas del 

```jsx
ros2 action send_goal AttachableJoint attachable_pkg/action/AttachModel "{parent: "AttachableLink_1_vehicle_1", child: "AttachableLink_1_box_1", attach: true}"

ros2 action send_goal AttachableJoint attachable_pkg/action/AttachModel "{parent: "AttachableLink_1_vehicle_1", child: "AttachableLink_1_box_1", attach: true}"
```

```jsx
ros2 action send_goal AttachableJoint attachable_pkg/action/AttachModel "{parent: "AttachableLink_1_wall_1", child: "AttachableLink_1_vehicle_1", attach: true}"

ros2 action send_goal AttachableJoint attachable_pkg/action/AttachModel "{parent_model: "rm2_1", parent_link: "AttachableLink_1_rm2_1", child_model: "rm2_2",child_link: "AttachableLink_1_rm2_2", attach: true}"

```

