using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GameState : MonoBehaviour
{
    public Client clientScript;
    public List<GameObject> watchTowers;
    public float minInterval = 5f;
    public float maxInterval = 10f;
    public bool spawnedPrisoner = false;

    void Start(){
        StartGame();
        StartCoroutine(RandomSpawner());
    }
    public async void StartGame(){
        //Debug.Log("StartGame called");
        await clientScript.StartGameSession();
    }

    public async void EndGame(){
        await clientScript.EndGameSession();
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
}
