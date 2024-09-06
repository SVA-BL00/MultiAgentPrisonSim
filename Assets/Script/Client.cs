using System;
using System.Collections;
using System.Collections.Generic;
using System.Threading.Tasks;
using SocketIOClient;
using SocketIOClient.Newtonsoft.Json;
using UnityEngine;
using Newtonsoft.Json.Linq;
using System.Threading;

public class Client : MonoBehaviour
{
    public SocketIOUnity socket;
    public DroneController droneController;

    private bool isGameSessionActive = false;
    private float reconnectDelay = 5f;
    private int maxReconnectAttempts = 5;
    private int currentReconnectAttempts = 0;
    private CancellationTokenSource cancellationTokenSource = new CancellationTokenSource();


    void Awake()
    {
        InitializeSocket();
    }

    private void InitializeSocket()
    {
        var uri = new Uri("http://localhost:5000");
        socket = new SocketIOUnity(uri, new SocketIOOptions
        {
            Query = new Dictionary<string, string>
                {
                    {"token", "UNITY" }
                },
            EIO = 4,
            Transport = SocketIOClient.Transport.TransportProtocol.WebSocket
        });
        socket.JsonSerializer = new NewtonsoftJsonSerializer();

        // Set up event handlers
        socket.OnConnected += (sender, e) =>
        {
            Debug.Log("Connected to server");
            currentReconnectAttempts = 0; // Reset reconnect attempts on successful connection
        };

        socket.OnDisconnected += (sender, e) =>
        {
            Debug.Log("Disconnected from server: " + e);
            if (isGameSessionActive)
            {
                StartCoroutine(TryReconnect());
            }
        };

        // AGENT ACTION CALL //
        socket.OnUnityThread("drone_response", (response) =>
        {
            string rawResponse = response.ToString();
            //Debug.Log("Raw DRONE server response: " + rawResponse);
            HandleDroneResponse(response);
        });
    }

    public async Task StartGameSession()
    {
        if (!isGameSessionActive)
        {
            isGameSessionActive = true;
            await ConnectAsync(cancellationTokenSource.Token);
            Debug.Log("Game session started");
        }
        else
        {
            Debug.Log("Game session is already active");
        }
    }

    public async Task EndGameSession()
    {
        if (isGameSessionActive)
        {
            isGameSessionActive = false;
            await DisconnectAsync(cancellationTokenSource.Token);
            Debug.Log("Game session ended");
        }
        else
        {
            Debug.Log("No active game session to end");
        }
    }

    public async Task ConnectAsync(CancellationToken token)
    {
        try
        {
            Debug.Log("Connecting to server asynchronously...");
            await socket.ConnectAsync();
        }
        catch (Exception ex)
        {
            Debug.LogError($"Error connecting to server asynchronously: {ex.Message}");
        }
    }

    public async Task DisconnectAsync(CancellationToken token)
    {
        try
        {
            Debug.Log("Disconnecting from server asynchronously...");
            await socket.DisconnectAsync();
        }
        catch (Exception ex)
        {
            Debug.LogError($"Error disconnecting from server asynchronously: {ex.Message}");
        }
    }

    private IEnumerator TryReconnect()
    {
        while (isGameSessionActive && currentReconnectAttempts < maxReconnectAttempts && !cancellationTokenSource.Token.IsCancellationRequested)
        {
            Debug.Log($"Attempting to reconnect... (Attempt {currentReconnectAttempts + 1}/{maxReconnectAttempts})");
            yield return new WaitForSeconds(reconnectDelay);

            var connectTask = ConnectAsync(cancellationTokenSource.Token);
            yield return new WaitUntil(() => connectTask.IsCompleted);

            if (socket.Connected)
            {
                Debug.Log("Reconnected successfully");
                yield break;
            }
            else
            {
                Debug.LogError("Reconnection attempt failed");
            }

            currentReconnectAttempts++;
        }

        if (currentReconnectAttempts >= maxReconnectAttempts)
        {
            Debug.LogError("Max reconnection attempts reached. Please check your connection and try again later.");
            isGameSessionActive = false;
        }
    }

    private void HandleDroneResponse(SocketIOResponse response)
    {
        try
        {
            var data = response.GetValue<JObject>();

            if (data != null && data.ContainsKey("command"))
            {
                string command = data["command"].ToString();
                //Debug.Log("Received command: " + command);
                droneController.ActionHandler(command);
            }
            else
            {
                Debug.LogWarning("Received invalid or empty response from server");
            }
        }
        catch (Exception ex)
        {
            Debug.LogError("Error parsing drone response: " + ex.Message);
        }
    }

    private void OnDestroy()
    {
        cancellationTokenSource.Cancel();
        EndGameSession();
    }

}
