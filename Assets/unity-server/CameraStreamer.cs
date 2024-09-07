using UnityEngine;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;
using System;

public class CameraStreamer : MonoBehaviour
{
    [Header("Cameras")]
    public Camera entityCamera;
    public Camera feedCamera;

    [Header("Server Configuration")]
    public string serverIP = "127.0.0.1";
    [SerializeField] public int serverPort = 5001; // Changed to match the server's port range

    private RenderTexture renderTexture;
    private Texture2D texture2D;
    private TcpClient client;
    private NetworkStream stream;
    private float frameInterval = 0.5f;
    private float timeSinceLastFrame = 0;
    private bool isConnected = false;

    private void Start()
    {
        Debug.Log("CameraStreamer: Start method called");
        if (feedCamera.enabled)
        {
            Debug.LogError("CameraStreamer: The 'feedCamera' must be disabled");
        }

        renderTexture = new RenderTexture(320, 320, 24); // Resized to match server's expected size
        texture2D = new Texture2D(320, 320, TextureFormat.RGB24, false);
        feedCamera.targetTexture = renderTexture;

        InitializeConnection();
        Debug.Log("CameraStreamer: Start method completed");
    }

    private void InitializeConnection()
    {
        Debug.Log("CameraStreamer: Initializing connection");
        try
        {
            client = new TcpClient(serverIP, serverPort);
            stream = client.GetStream();
            isConnected = true;
            Debug.Log($"CameraStreamer: Connected to server on port {serverPort}");
        }
        catch (SocketException e)
        {
            Debug.LogError($"CameraStreamer: Failed to connect to server: {e.Message}");
            isConnected = false;
        }
        catch (Exception e)
        {
            Debug.LogError($"CameraStreamer: Unexpected error in InitializeConnection: {e.Message}");
            isConnected = false;
        }
    }

    private void Update()
    {
        if (!isConnected)
        {
            Debug.Log("CameraStreamer: Not connected, attempting reconnection");
            AttemptReconnection();
            return;
        }

        feedCamera.transform.position = entityCamera.transform.position;
        feedCamera.transform.rotation = entityCamera.transform.rotation;

        timeSinceLastFrame += Time.deltaTime;
        if (timeSinceLastFrame >= frameInterval)
        {
            timeSinceLastFrame = 0;
            _ = CaptureAndSendFrameAsync();
        }
    }

    private void AttemptReconnection()
    {
        Debug.Log("CameraStreamer: Attempting to reconnect...");
        InitializeConnection();
    }

    private async Task CaptureAndSendFrameAsync()
    {
        await Task.Yield();

        feedCamera.Render();
        RenderTexture.active = renderTexture;
        
        Rect rect = new Rect(0, 0, renderTexture.width, renderTexture.height);
        texture2D.ReadPixels(rect, 0, 0);
        texture2D.Apply();

        byte[] bytes = texture2D.EncodeToJPG();

        var length = Encoding.UTF8.GetBytes(bytes.Length.ToString("D7"));
        await stream.WriteAsync(length, 0, length.Length);
        await stream.WriteAsync(bytes, 0, bytes.Length);

        RenderTexture.active = null;
    }

    private void OnApplicationQuit()
    {
        Debug.Log("CameraStreamer: Application quitting, closing connection");
        if (client != null && client.Connected)
        {
            client.Close();
        }
    }
}