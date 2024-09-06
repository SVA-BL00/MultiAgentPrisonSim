using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CatAnimController : MonoBehaviour
{
    [SerializeField] public Animator CA;
    [SerializeField] public GameObject FACE;
    public List<GameObject> cameras;
    private bool hasDetected = false;
    private bool Triggered = false;
    private Renderer rend;
    public int materialIndex = 1;
    public Vector2 eyesSurprise = new Vector2(0.25f, 0f);
    public Vector2 eyesClosed = new Vector2(0.75f, 0f);
    void Start()
    {
        rend = FACE.GetComponent<Renderer>();
        StartCoroutine(Sleep());
    }

    void Update(){
        if(!Triggered){
            CheckAlarm();
            if(hasDetected){
                StopAllCoroutines();
                CA.SetBool("isSleepy", false);
                CA.SetBool("isWorried", true);
                ChangeFace(eyesSurprise);
                Triggered = true;
            }
        }
    }

    IEnumerator Sleep(){
        while(true){
            yield return new WaitForSeconds(5f);
            CA.SetBool("isSleepy", true);
            ChangeFace(eyesClosed);
        }
    }

    void ChangeFace(Vector2 newFace){
        Material targetMaterial = rend.materials[1];
        targetMaterial.mainTextureOffset = newFace;
    }


    // USED SOLELY FOR ANIMATION PURPOSES
    void CheckAlarm(){
        for(int i = 0; i < cameras.Count; i++){
            if(cameras[i].GetComponent<CameraDetector>().isDetected){
                hasDetected = true;
            }
        }
    }
}
