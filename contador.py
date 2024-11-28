import flet as ft
import requests

#URL="http://127.0.0.1:5000/evento"
URL="https://actividad02.onrender.com/evento"
URL_TABLA="https://actividad02.onrender.com/vista"
URL_ELIMINAR="https://actividad02.onrender.com/eliminar"

def main(page: ft.Page):
    page.bgcolor="#26e5ee"
    page.scroll = "auto"
    page.update()
    t = ft.Text()
    loading=ft.Text("cargando", size=20, color="blue",visible=False)
    def eliminar(id):
        try:
            response = requests.post(f"https://actividad02.onrender.com/eliminar/{id}")
            if response.status_code==200:
                print(f"SE ELIMINO EL REGRISTO DEL ID {id}")
                cargar()
            else:
                print(f"error")
        except requests.exceptions.RequestException as e:
                print(f"Error de solicitud: {str(e)}") 
                t.value = f"Error al conectar con el servidor: {str(e)}"

        
    def button_clicked(e):
        nombre=txtnombre.value
        calificacion= txtcalificacion.value
        comentario=txtcomentario.value

        if not nombre:
            t.value= "El campo de 'nombre' es obligatorio"
        elif len(nombre)<10 or len(nombre)>50:
             t.value= "El campo de 'nombre' debe de tener entre 10 y 50 caracteres"
        elif not calificacion.isdigit() or not(1<=int(calificacion)<=5):
            t.value= "El campo de 'calificación' es obligatorio y tiene que ser de 1 a 5"
        elif not comentario:
            t.value= "El campo de 'comentario' es obligatorio"
        elif len(comentario)<10 or len(comentario)>50:
             t.value= "El campo de 'comentario' debe de tener entre 10 y 50 caracteres"
        else:  
            data={
                'txtnombreApellido':nombre,
                'txtcalificacion':calificacion,
                'txtcomentario':comentario
            }
            try:
                print("Enviando datos...") 
                response=requests.post(URL,data=data)

                if response.status_code==200:
                    print("Respuesta del servidor: Éxito")
                    t.value="¡Encuesta enviada exitosamente!"

                else: 
                    print(f"Error en la respuesta: {response.status_code}")
                    t.value="¡Ups Hubo un error!"
            except requests.exceptions.RequestException as e:
                print(f"Error de solicitud: {str(e)}") 
                t.value = f"Error al conectar con el servidor: {str(e)}"
            #t.value = f"Datos enviados:  '{txtnombre.value}', '{txtcalificacion.value}','{txtcomentario.value}'."
        page.update()
    
    titulo=ft.Text(
        "Encuesta de calificación",
        size=30,
        weight="bold",
        color="#FFD700"
    )
    def cargar():
        loading.visible=True
        page.update()
        try:
             response = requests.get(URL_TABLA)
             if response.status_code==200:
                   registros=response.json()
                   if registros:
                        rows=[]
                        for registro in registros:
                             #lista.append(ft.Text(f"Nombre: {registro[1]}, comentario:  {registro[2]}, Calificación: {registro[3]}"))
                                rows.append(
                                        ft.DataRow(
                                            cells=[
                                                ft.DataCell(ft.Text(registro[1])),
                                                ft.DataCell(ft.Text(registro[3])),
                                                ft.DataCell(ft.Text(registro[2])),
                                                ft.DataCell(ft.IconButton(
                                                    icon=ft.icons.DELETE_FOREVER,
                                                    on_click=lambda e, id=registro[0]: eliminar(id),
                                                   
                                                )

                                                ),
                                            ]
                                        )
                                )
                        tabla=ft.DataTable(
                                width=900,
                                border=ft.border.all(1, "#cacaca"),
                                border_radius=8,
                                bgcolor="white",
                                horizontal_lines=ft.BorderSide(1, "#cacaca"),
                                
                                columns=[
                                    ft.DataColumn(ft.Text("NOMBRE")),
                                    ft.DataColumn(ft.Text("CALIFICACIÓN")),
                                    ft.DataColumn(ft.Text("COMENTARIO")),
                                    ft.DataColumn(ft.Text("ACCIÓN")),
                                   
                                ],
                                rows=rows        
                        )
                        
                        registros_v.controls=[tabla]
                   else:
                        registros_v.controls = [ft.Text("No se encontraron registros")]
                             
             else:
                registros_v.controls = [ft.Text(f"Error al obtener los datos: {response.status_code}")]
        except requests.exceptions.RequestException as e:
                print(f"Error de solicitud: {str(e)}") 
                registros_v.controls = [ft.Text(f"Error al conectar con el servidor: {str(e)}")]
        loading.visible=False
        page.update()

    registros_v=ft.Column ()
    btncargardatos= ft.ElevatedButton(
         text="Ver calificaciones", 
         on_click=lambda e: cargar(), 
         color="black", bgcolor="#e8f6f7",
          icon="Star",
            icon_color="black" , width=700, height=40,)
    txtnombre = ft.TextField(
        label="Ingresa tu nombre y apellido", 
        icon=ft.icons.PERSON,
        border_color="blue")
    txtcalificacion = ft.TextField(label="Ingresa tu calificación", icon=ft.icons.STARS,
        border_color="blue")
    txtcomentario = ft.TextField(label="Ingresa tu comentario", icon=ft.icons.COMMENT, border_color="blue")
    b = ft.ElevatedButton(text="Enviar calificación", on_click=button_clicked, color="blue", bgcolor="yellow", width=700, height=40,)
    
    '''
    card=ft.Card(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Titulo de la tarjeta", size=20, weight="bold"),
                    ft.Text("Es un ejemplo"),
                    ft.ElevatedButton(text="Botón", on_click=lambda e: print("Botón en la tarjeta presionado")),
                    
                ]
            ),
            width=400,
            padding=10,
            bgcolor="lightblue",
            border_radius=12,
            
        )
    )'''

  

    contenedor=ft.Container(
   
            content=ft.Column(
                controls=[titulo, txtnombre,txtcalificacion, txtcomentario, t,b, btncargardatos, registros_v],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
               
                

            ),bgcolor="white", padding=10, border_radius=10, expand=True
   
    )
    '''responsivo=ft.ResponsiveRow([
        ft.Column(col={"sm": 12, "md": 6}, controls=[titulo]),
        ft.Column(col={"sm": 12, "md": 6}, controls=[txtnombre]),
        ft.Column(col={"sm": 12, "md": 6}, controls=[txtcalificacion]),
        ft.Column(col={"sm": 12, "md": 6}, controls=[txtcomentario]),
        ft.Column(col={"sm": 12, "md": 6}, controls=[b]),
        ft.Column(col={"sm": 12, "md": 6}, controls=[btncargardatos]),
        ft.Column(col={"sm": 12, "md": 6}, controls=[registros_v]),
        ft.Column(col={"sm": 12, "md": 6}, controls=[t]),
    ])

    contenedor.content=responsivo
    '''
    page.add(contenedor)

ft.app(main)