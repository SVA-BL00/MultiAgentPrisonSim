using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AlarmWatchTower : MonoBehaviour
{
    public List<GameObject> cameras;
    [SerializeField] public Light towerLight;
    bool Triggered = false;
    bool hasDetected = false;
    private Color[] colors;
    void Start()
    {
        colors = new Color[2];
        colors[0] = new Color(1,0,0);
        colors[1] = new Color(1,1,1);
    }

    // Update is called once per frame
    void Update(){
        if(!Triggered){
            CheckAlarm();
            if(hasDetected){
                StartCoroutine(Siren());
                Triggered = true;
            }
        }
    }

    // USED SOLELY FOR ANIMATION PURPOSES
    void CheckAlarm(){
        for(int i = 0; i < cameras.Count; i++){
            if(cameras[i].GetComponent<CameraDetector>().isDetected){
                hasDetected = true;
            }
        }
    }

    IEnumerator Siren(){
        int colorIndex = 0;
        while (true){
            towerLight.color = colors[colorIndex];
            colorIndex = (colorIndex + 1) % colors.Length;
            yield return new WaitForSeconds(0.3f);
        }
    }
}
