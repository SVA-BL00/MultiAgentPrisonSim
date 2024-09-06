using UnityEngine;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using System.Threading;
using System;

public class CameraStreamer : MonoBehaviour
{
    [Header("Cameras")]
    public Camera entityCamera;
    public Camera feedCamera;

    [Header("Server Configuration")]
    public string serverIP = "127.0.0.1";
    [SerializeField] public int serverPort = 5000;

    private RenderTexture renderTexture;
    private Texture2D texture2D;
    private TcpClient client;
    private NetworkStream stream;
    private float frameInterval = 0.5f; // Increased interval to reduce load
    private float timeSinceLastFrame = 0;
    private bool isConnected = false;

    [SerializeField] public GameObject Camera;
    CameraDetector cameraDetector;

    private void Awake()
    {
        Debug.Log("CameraStreamer: Awake method called");
        try
        {
            cameraDetector = Camera.GetComponent<CameraDetector>();
            Debug.Log("CameraStreamer: CameraDetector component found");
        }
        catch (Exception e)
        {
            Debug.LogError($"CameraStreamer: Error in Awake: {e.Message}");
        }
    }

    private async void Start()
    {
        Debug.Log("CameraStreamer: Start method called");
        if (feedCamera.enabled)
        {
            Debug.LogError("CameraStreamer: The 'feedCamera' must be disabled");
        }

        InitializeConnection();
        InitializeTextures();
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

    private void InitializeTextures()
    {
        Debug.Log("CameraStreamer: Initializing textures");
        try
        {
            renderTexture = new RenderTexture(entityCamera.pixelWidth / 2, entityCamera.pixelHeight / 2, 24);
            feedCamera.targetTexture = renderTexture;
            texture2D = new Texture2D(renderTexture.width, renderTexture.height, TextureFormat.RGB24, false);
            Debug.Log("CameraStreamer: Textures initialized successfully");
        }
        catch (Exception e)
        {
            Debug.LogError($"CameraStreamer: Error initializing textures: {e.Message}");
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
            Debug.Log("CameraStreamer: Frame interval reached, capturing and sending frame");
            timeSinceLastFrame = 0;
            _ = CaptureAndSendFrameAsync();  // Fire and forget
        }
    }

    private void AttemptReconnection()
    {
        Debug.Log("CameraStreamer: Attempting to reconnect...");
        InitializeConnection();
    }

    private async Task CaptureAndSendFrameAsync()
    {
        Debug.Log("CameraStreamer: Starting CaptureAndSendFrameAsync");
        try
        {
            byte[] buffer = new byte[1];
            int bytesRead = 0;

            using (var cts = new CancellationTokenSource(TimeSpan.FromSeconds(2))) // 2-second timeout
            {
                Debug.Log("CameraStreamer: Waiting for server response...");
                try
                {
                    bytesRead = await stream.ReadAsync(buffer, 0, buffer.Length, cts.Token);
                    Debug.Log($"CameraStreamer: Read operation completed. Bytes read: {bytesRead}");
                }
                catch (OperationCanceledException)
                {
                    Debug.LogWarning("CameraStreamer: Read operation timed out after 2 seconds");
                    return;
                }
            }

            if (bytesRead > 0)
            {
                Debug.Log($"CameraStreamer: Received byte value: {buffer[0]}");
                bool bunnyDetected = buffer[0] == 1;
                if (cameraDetector != null)
                {
                    cameraDetector.isDetected = bunnyDetected;
                    Debug.Log($"CameraStreamer: Bunny detected: {bunnyDetected}");
                }
                else
                {
                    Debug.LogError("CameraStreamer: cameraDetector is null");
                }
            }
            else
            {
                Debug.LogWarning("CameraStreamer: No data was read from the stream.");
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"CameraStreamer: Error in ReceiveDetectionStatusAsync: {e.Message}");
            isConnected = false;
        }
        finally
        {
            Debug.Log("CameraStreamer: ReceiveDetectionStatusAsync completed");
        }
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