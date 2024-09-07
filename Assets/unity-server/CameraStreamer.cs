using UnityEngine;
using System.Net.Sockets;
using System.Net;
using System.Text;
using System;

public class CameraStreamer : MonoBehaviour
{
    [Header("Cameras")]
    public Camera entityCamera;
    public Camera feedCamera;

    [Header("Server Configuration")]
    public string serverIP = "127.0.0.1";
    [SerializeField] public int serverPort = 5001;

    [Header("Detection")]
    public CameraDetector detector;
    private RenderTexture renderTexture;
    private Texture2D texture2D;
    private TcpClient client;
    private NetworkStream stream;
    private UdpClient udpClient;
    private float frameInterval = 0.5f;
    private float timeSinceLastFrame = 0;
    private bool isConnected = false;

    private void Start()
    {
        if(feedCamera.enabled){
            Debug.LogError("CameraStreamer: The 'feedCamera' must be disabled");
        }

        renderTexture = new RenderTexture(320, 320, 24);
        texture2D = new Texture2D(320, 320, TextureFormat.RGB24, false);
        feedCamera.targetTexture = renderTexture;

        InitializeConnection();
        InitializeUdpListener();

        if(detector == null){
            detector = GetComponent<CameraDetector>();
            if (detector == null){
                Debug.LogError("CameraStreamer: CameraDetector component not found!");
            }
        }
    }

    private void InitializeConnection()
    {
        try{
            client = new TcpClient(serverIP, serverPort);
            stream = client.GetStream();
            isConnected = true;
            Debug.Log($"CameraStreamer: Connected to server on port {serverPort}");
        }catch (SocketException e){
            Debug.LogError($"CameraStreamer: Failed to connect to server: {e.Message}");
            isConnected = false;
        }
    }

    private void InitializeUdpListener(){
        udpClient = new UdpClient(serverPort);
        udpClient.BeginReceive(new AsyncCallback(ReceiveCallback), null);
    }

    private void ReceiveCallback(IAsyncResult ar){
        IPEndPoint ip = new IPEndPoint(IPAddress.Any, serverPort);
        byte[] bytes = udpClient.EndReceive(ar, ref ip);
        string message = Encoding.ASCII.GetString(bytes);

        if(message == "BUNNY"){
            if(detector != null){
                detector.isDetected = true;
            }else{
                Debug.LogError("CameraStreamer: CameraDetector is null, can't update detection status");
            }
        }

        udpClient.BeginReceive(new AsyncCallback(ReceiveCallback), null);
    }

    private void Update(){
        if(!isConnected){
            AttemptReconnection();
            return;
        }

        feedCamera.transform.position = entityCamera.transform.position;
        feedCamera.transform.rotation = entityCamera.transform.rotation;

        timeSinceLastFrame += Time.deltaTime;
        if(timeSinceLastFrame >= frameInterval){
            timeSinceLastFrame = 0;
            CaptureAndSendFrame();
        }
    }

    private void AttemptReconnection(){
        Debug.Log("CameraStreamer: Attempting to reconnect...");
        InitializeConnection();
    }

    private void CaptureAndSendFrame(){
        feedCamera.Render();
        RenderTexture.active = renderTexture;
        
        Rect rect = new Rect(0, 0, renderTexture.width, renderTexture.height);
        texture2D.ReadPixels(rect, 0, 0);
        texture2D.Apply();

        byte[] bytes = texture2D.EncodeToJPG();

        var length = Encoding.UTF8.GetBytes(bytes.Length.ToString("D7"));
        stream.Write(length, 0, length.Length);
        stream.Write(bytes, 0, bytes.Length);

        RenderTexture.active = null;
    }

    private void OnApplicationQuit(){
        if (client != null && client.Connected){
            client.Close();
        }if (udpClient != null){
            udpClient.Close();
        }
    }
}