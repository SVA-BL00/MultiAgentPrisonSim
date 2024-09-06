using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CameraDetector : MonoBehaviour
{
    public receiver receiver;
    public bool isDetected = false;
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        if (receiver != null && receiver.bunnyDetected)
    {
        isDetected = true;
    }
    }
}
