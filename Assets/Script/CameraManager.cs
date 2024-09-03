using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CameraManager : MonoBehaviour
{
    public List<GameObject> cameras;
    private int counterCamera = 0;
    void Start()
    {
        ChangeCamera();
    }

    void Update()
    {
        if(Input.GetKeyDown(KeyCode.Z)){
            ChangeCamera();
        }
    }
    void ChangeCamera(){
        for(int i = 0; i < cameras.Count; i++){
            cameras[i].SetActive(false);
        }

        if(counterCamera != 0 || counterCamera != 2){
            cameras[1].SetActive(true);
            cameras[2].SetActive(true);
            cameras[3].SetActive(true);
            cameras[4].SetActive(true);
        }

        cameras[counterCamera].SetActive(true);

        if(counterCamera == 2){
            cameras[5].SetActive(true);
        }

        counterCamera = (counterCamera + 1) % 3;
    }
}
