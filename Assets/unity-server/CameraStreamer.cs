using UnityEngine;
using System.Collections;
using System.Net.Sockets;
using System.Text;
using System.Threading;

public class CameraStreamer : MonoBehaviour
{
    [Header("Cameras")]
    public Camera entityCamera;
    public Camera feedCamera;

    [Header("Server Configuration")]
    public string serverIP = "127.0.0.1";
    [SerializeField] public int serverPort = 5000; // Changed to match one of the server ports

    private RenderTexture renderTexture;
    private Texture2D texture2D;
    private TcpClient client;
    private NetworkStream stream;
    private float frameInterval = 0.1f;
    private float timeSinceLastFrame = 0;
    private bool isConnected = false;

    private CameraDetector cameraDetector;

    private void Awake()
    {
        cameraDetector = GetComponent<CameraDetector>();
    }

    private void Start()
    {
        if (feedCamera.enabled)
        {
            Debug.LogError("The 'feedCamera' must be disabled");
        }

        InitializeConnection();
        InitializeTextures();
    }

    private void InitializeConnection()
    {
        try
        {
            client = new TcpClient(serverIP, serverPort);
            stream = client.GetStream();
            isConnected = true;
            Debug.Log($"Connected to server on port {serverPort}");
        }
        catch (SocketException e)
        {
            Debug.LogError($"Failed to connect to server: {e.Message}");
            isConnected = false;
        }
    }

    private void InitializeTextures()
    {
        renderTexture = new RenderTexture(entityCamera.pixelWidth, entityCamera.pixelHeight, 24);
        feedCamera.targetTexture = renderTexture;
        texture2D = new Texture2D(renderTexture.width, renderTexture.height, TextureFormat.RGB24, false);
    }

    private void Update()
    {
        if (!isConnected)
        {
            AttemptReconnection();
            return;
        }

        feedCamera.transform.position = entityCamera.transform.position;
        feedCamera.transform.rotation = entityCamera.transform.rotation;

        timeSinceLastFrame += Time.deltaTime;
        if (timeSinceLastFrame >= frameInterval)
        {
            timeSinceLastFrame = 0;
            StartCoroutine(CaptureAndSendFrame());
        }
    }

    private void AttemptReconnection()
    {
        Debug.Log("Attempting to reconnect...");
        InitializeConnection();
    }

    private IEnumerator CaptureAndSendFrame()
{
    yield return new WaitForEndOfFrame();

    // Render the feed camera and capture the frame
    feedCamera.Render();
    texture2D.ReadPixels(new Rect(0, 0, renderTexture.width, renderTexture.height), 0, 0);
    texture2D.Apply();

    // Convert the texture to a JPG byte array
    byte[] bytes = texture2D.EncodeToJPG();

    try
    {
        // Send the length of the frame (7 bytes as a string) - Image only
        byte[] lengthBytes = Encoding.UTF8.GetBytes(bytes.Length.ToString().PadLeft(7, '0'));
        stream.Write(lengthBytes, 0, lengthBytes.Length);

        // Log the frame size for debugging
        Debug.Log($"Sending frame of size: {bytes.Length}");

        // Send the actual frame data (Image data)
        stream.Write(bytes, 0, bytes.Length);

        // After sending the frame, we expect to receive detection status
        ReceiveDetectionStatus();
    }
    catch (SocketException e)
    {
        Debug.LogError($"Connection lost: {e.Message}");
        isConnected = false;
    }
}


private void ReceiveDetectionStatus()
{
    try
    {
        // Buffer to receive 1 byte (status byte)
        byte[] buffer = new byte[1];  // Expecting 1 byte for the status
        int bytesRead = stream.Read(buffer, 0, buffer.Length);

        if (bytesRead > 0)
        {
            // Log the received byte for debugging
            Debug.Log($"Received status byte: {buffer[0]}");

            // Check if the buffer contains '1' (bunny detected) or '0' (no bunny detected)
            bool bunnyDetected = buffer[0] == 1;
            cameraDetector.isDetected = bunnyDetected;  // Update detection status in Unity
            Debug.Log($"Bunny detected: {bunnyDetected}");
        }
        else
        {
            Debug.LogWarning("No detection status received");
        }
    }
    catch (SocketException e)
    {
        Debug.LogError($"Error receiving detection status: {e.Message}");
        isConnected = false;
    }
}




    private void OnApplicationQuit()
    {
        if (client != null && client.Connected)
        {
            client.Close();
        }
    }
}