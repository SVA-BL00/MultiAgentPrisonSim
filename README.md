# Multi-agent prison simulator
![image](https://github.com/user-attachments/assets/c37d8120-7de5-418e-be68-45aec0d99a22)
## ENG
### Project description
To simulate coordinated patrolling in a high-risk area, a multi-agent system was implemented using Unity for graphical visualization. The penitentiary is monitored by static security cameras, a drone, and security personnel.
The cameras and the drone use computer vision to detect suspicious activities. The drone is alerted when a camera detectes suspicious activity, and if the drone also identifies this anomaly, the security personnel takes over to verify the situation.
### Installation
1. Ensure that SocketIO unity is installed. In case it's not present in the project's Package Manager, add the following link:
```https://github.com/itisnajim/SocketIOUnity.git```
2. From a code editor, find the projet's folder. Enter the Script directory:
```
cd Assets/Script
```
3. Install the following libraries to run the web socket and agentpy, using pip install.
- Flask
- flask_socketio
4. Run the web socket
```
python app.py
```
5. Run SampleScene in unity
## ESP
### Descripción de proyecto
Para simular el patrullaje coordinado en una zona de riesgo, se implementó un sistema multiagente, utilizando Unity para la visualización gráfica.
El centro penitenciario es vigilado por cámaras de seguridad estáticas, un dron, y personal de seguridad.
Para evitar la fuga de los internos, tanto las cámaras como el dron utilizan visión computacional, que informan si detecta una sospecha.
Cuando una cámara detecta una anomalía, envía una alerta al dron. Si el dron también identifica una sospecha, el personal de seguridad se coordina con el dron para verificar la situación.
### Instalación
1. Es importante asegurarse que SocketIO unity esté instalado. Aunque debería de estar en Package Manager, en caso de no estar, agregar el siguiente paquete:
```https://github.com/itisnajim/SocketIOUnity.git```
2. Desde un editor de código, entrar a la carpeta del proyecto. Entrar a Script:
```
cd Assets/Script
```
3. Instalar las librerías necesarias para correr el web socket y agentpy con pip install.
- Flask
- flask_socketio
4. Correr el web socket
```
python app.py
```
5. Correr SampleScene en Unity
