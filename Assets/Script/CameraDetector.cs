using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using Newtonsoft.Json.Linq;
using UnityEngine;

public class CameraDetector : MonoBehaviour
{
    private TcpListener server;
    [SerializeField]public int port;
    //public receiver receiver;
    public bool isDetected = false;
    void Start()
    {
        server = new TcpListener(IPAddress.Loopback, port);
        server.Start();
        server.BeginAcceptTcpClient(new AsyncCallback(OnClientConnect), null);
    }

    void OnClientConnect(IAsyncResult ar)
    {
        TcpClient client = server.EndAcceptTcpClient(ar);
        NetworkStream stream = client.GetStream();

        byte[] buffer = new byte[1024];
        int bytesRead = stream.Read(buffer, 0, buffer.Length);
        string data = Encoding.UTF8.GetString(buffer, 0, bytesRead);

        JObject json = JObject.Parse(data);
        bool bunnyDetected = json["bunny_detected"].ToObject<bool>();

        if (bunnyDetected)
        {
            Debug.Log("Bunny detected!");
            isDetected = true;
        }
        else
        {
            Debug.Log("No bunny detected.");
        }

        stream.Close();
        client.Close();
    }

    void OnApplicationQuit()
    {
        server.Stop();
    }
}
