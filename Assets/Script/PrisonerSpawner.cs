using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PrisonerSpawner : MonoBehaviour
{
    public GameObject prisonerPF;
    [SerializeField] private float minSpawnPosX = 5f;
    [SerializeField] private float maxSpawnPosX= 10f;
    [SerializeField] private float minSpawnPosZ = 5f;
    [SerializeField] private float maxSpawnPosZ = 10f;
    public void Spawn(){
        Vector3 spawnPos = new Vector3(Random.Range(minSpawnPosX, maxSpawnPosX), 0f, Random.Range(minSpawnPosZ, maxSpawnPosZ));
        Quaternion randomRotation = Quaternion.Euler(0f, Random.Range(0f, 360f), 0f);
        Instantiate(prisonerPF, spawnPos, randomRotation);
    }
}