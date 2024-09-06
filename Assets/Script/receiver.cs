using UnityEngine;
using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using Unity.VisualScripting;

public class receiver : MonoBehaviour
{
    [SerializeField]public int port = 5000; // Make sure this matches the port you're using in Python
    private UdpClient udpClient;
    private Thread receiveThread;
    private bool isRunning = false;

    public bool bunnyDetected = false;

    void Start()
    {
        InitializeUDPListener();
    }

    void InitializeUDPListener()
    {
        udpClient = new UdpClient(port);
        isRunning = true;
        receiveThread = new Thread(new ThreadStart(ReceiveData));
        receiveThread.IsBackground = true;
        receiveThread.Start();
        Debug.Log($"UDP listener started on port {port}");
    }

    private void ReceiveData()
    {
        while (isRunning)
        {
            try
            {
                IPEndPoint remoteEndPoint = new IPEndPoint(IPAddress.Any, 0);
                byte[] data = udpClient.Receive(ref remoteEndPoint);
                string message = Encoding.UTF8.GetString(data);
                bunnyDetected = message == "1";
                Debug.Log($"Received: {message}, Bunny detected: {bunnyDetected}");
            }
            catch (Exception e)
            {
                Debug.LogError($"Error receiving UDP data: {e.Message}");
            }
        }
    }

    void OnDisable()
    {
        isRunning = false;
        if (receiveThread != null && receiveThread.IsAlive)
        {
            receiveThread.Abort();
        }
        if (udpClient != null)
        {
            udpClient.Close();
        }
    }
}