using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CameraDetector : MonoBehaviour
{
    public bool isDetected = false;
    public GameState gs;
    void Start()
    {
    }

    void Update(){
        if(isDetected){
            gs.detectedPrisoner = true;
        }
    }
}
