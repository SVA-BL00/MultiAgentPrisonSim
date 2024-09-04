using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;

public class CameraManager : MonoBehaviour
{
    public List<GameObject> cameras;
    [SerializeField] TMP_Text cameraTitle;
    public CanvasGroup fadeCanvasGroup;
    public float fadeDuration = 0.2f;
    private int counterCamera = 0;
    private bool isFading = false;
    void Start()
    {
        ChangeCamera();
    }

    void Update()
    {
        if(Input.GetKeyDown(KeyCode.Z) && !isFading){
            StartCoroutine(ChangeWithFade());
        }
    }

    IEnumerator ChangeWithFade(){
        isFading = true;
        yield return StartCoroutine(Fade(1f));

        ChangeCamera();
        yield return StartCoroutine(Fade(0f));
        isFading = false;
    }

    IEnumerator Fade(float targetAlpha){
        float startAlpha = fadeCanvasGroup.alpha;
        float elapsedTime = 0f;

        while (elapsedTime < fadeDuration){
            fadeCanvasGroup.alpha = Mathf.Lerp(startAlpha, targetAlpha, elapsedTime / fadeDuration);
            elapsedTime += Time.deltaTime;
            yield return null;
        }

        fadeCanvasGroup.alpha = targetAlpha;
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
            cameraTitle.text = "CCTV";
            
        }

        cameras[counterCamera].SetActive(true);

        if(counterCamera == 2){
            cameras[5].SetActive(true);
            cameraTitle.text = "Pawlice cam";
        }else if(counterCamera == 0){
            cameraTitle.text = "Drone cam";
        }

        counterCamera = (counterCamera + 1) % 3;
    }
}
