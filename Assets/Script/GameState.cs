using System.Collections;
using System.Collections.Generic;
using TMPro;
using Unity.VisualScripting;
using UnityEngine;

public class GameState : MonoBehaviour
{
    public Client clientScript;
    public List<GameObject> watchTowers;
    public float minInterval = 10f;
    public float maxInterval = 15f;
    public bool spawnedPrisoner = false;
    public bool detectedPrisoner = false;
    [SerializeField] GameObject alert;
    [SerializeField] GameObject endText;

    void Start(){
        StartGame();
        StartCoroutine(RandomSpawner());
    }
    public async void StartGame(){
        //Debug.Log("StartGame called");
        await clientScript.StartGameSession();
    }

    public async void EndGame(){
        endText.SetActive(true);
        await clientScript.EndGameSession();

        #if UNITY_EDITOR
        UnityEditor.EditorApplication.isPlaying = false;
        #else
        Application.Quit();
        #endif
    }

    IEnumerator RandomSpawner(){
        while(true){
            if(spawnedPrisoner){
                yield break;
            }

            float randomDelay = Random.Range(minInterval, maxInterval);
            yield return new WaitForSeconds(randomDelay);
            SpawnPrisoner();
        }
    }
    public void SpawnPrisoner(){
        int randomT = Random.Range(0,4);
        PrisonerSpawner toSpawn = watchTowers[randomT].GetComponent<PrisonerSpawner>();
        toSpawn.Spawn();
        spawnedPrisoner = true;
    }
    void Update(){
        if(detectedPrisoner){
            alert.SetActive(true);
        }
    }

}
