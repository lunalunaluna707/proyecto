import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_correo_mantenimiento(nombre, horometro, fecha, descripcion, recipient_email):

    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "vazquezmariana125670@gmail.com"
    sender_password = "mglplmskljookhlj"

  
    subject = "Registro de Mantenimiento"
    body = f"""
    Se ha registrado un nuevo mantenimiento:

    - Máquina: {nombre}
    - Fecha: {fecha}
    - Horómetro: {horometro}
    - Descripción: {descripcion}

    Puedes consultar más detalles en el siguiente enlace:
    https://proyecto-n4r4.onrender.com/tablamantenimiento

    Atentamente,
    Equipo de Gestión de Mantenimiento
    """
 
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        print("Correo enviado exitosamente.")
    except Exception as e:
        raise RuntimeError(f"Error enviando correo: {e}")
