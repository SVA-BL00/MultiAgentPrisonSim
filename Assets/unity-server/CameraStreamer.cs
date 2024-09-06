using UnityEngine;
using System.Collections;
using System.Net.Sockets;
using System.Net.Http.Headers;
using System.Linq;

public class CameraStreamer : MonoBehaviour
{
    [Header("Camaras")] [Tooltip("Referencia a la camara del jugador o entidad")]
    public Camera entityCamera;

    [Header("Camaras")] [Tooltip("Referencia a la camara que se va a usar para renderizar el frame (debe estar deshabilitada)")]
    public Camera feedCamera;

    [Header("Configuraciones")] [Tooltip("IP del servidor de python")]
    public string serverIP = "127.0.0.1";

    [Header("Configuraciones")] [Tooltip("Puerto del servidor de python")]
    [SerializeField] public int serverPort = 5000;

    // textura donde se va a renderizar la camara
    private RenderTexture renderTexture;

    // textura que se va a enviar al servidor de python
    private Texture2D texture2D;

    // conexion con el servidor
    private TcpClient client;

    // flujo de datos de la conexion
    private NetworkStream stream;

    private float frameInterval = 0.1f; // 100 ms
    private float timeSinceLastFrame = 0;
    void Start()
    {
        // asegurarnos que la camara de python este deshabilitada
        if (feedCamera.enabled) {
            Debug.LogError("La camara 'feedCamera' debe estar deshabilitada");
        }

        // crear conexion con el servidor
        client = new TcpClient(serverIP, serverPort);

        // establecer conexion con el servidor
        stream = client.GetStream();

        // crear textura con dimensiones de la camara
        renderTexture = new RenderTexture(entityCamera.pixelWidth, entityCamera.pixelHeight, 24);

        // textura donde se va a renderizar la camara
        feedCamera.targetTexture = renderTexture;

        // textura que se va a enviar al servidor de python
        texture2D = new Texture2D(renderTexture.width, renderTexture.height, TextureFormat.RGB24, false);

        
    }

    void Update()
    {
        // copiar posicion y rotacion de la camara del jugador a la camara de la feed
        feedCamera.transform.position = entityCamera.transform.position;
        feedCamera.transform.rotation = entityCamera.transform.rotation;

        // si la conexion con el servidor esta establecida, capturar y enviar frame
        if (client.Connected)
        {
            timeSinceLastFrame += Time.deltaTime;
            if (timeSinceLastFrame >= frameInterval)
            {
                timeSinceLastFrame = 0;
                StartCoroutine(CaptureAndSendFrame());
            }
        }
    }

    IEnumerator CaptureAndSendFrame()
    {
        yield return new WaitForEndOfFrame();

        // redenderizar la camara en la textura
        feedCamera.Render();

        // leer pixeles de la textura
        texture2D.ReadPixels(new Rect(0, 0, renderTexture.width, renderTexture.height), 0, 0);
        texture2D.Apply();

        // convertir textura a bytes en formato jpg
        byte[] bytes = texture2D.EncodeToJPG();

        // enviar cantidad de bytes en la imagen
        var length = System.Text.Encoding.UTF8.GetBytes(bytes.Length.ToString());
        stream.Write(length, 0, length.Length);

        // enviar bytes de la imagen
        stream.Write(bytes, 0, bytes.Length);
    }

    void OnApplicationQuit()
    {
        if (client != null && client.Connected)
        {
            client.Close();
        }
    }
}