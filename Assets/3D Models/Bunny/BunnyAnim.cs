using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BunnyAnim : MonoBehaviour
{
    [SerializeField] public Animator BA;
    [SerializeField] public GameObject FACE;
    private Renderer rend;
    public int materialIndex = 0;
    public Vector2 eyesSurprise = new Vector2(0.25f, 0f);
    public Vector2 eyesClosed = new Vector2(0.75f, 0f);
    void Start()
    {
        rend = FACE.GetComponent<Renderer>();
    }

    void OnCollisionEnter(Collision collision){
        BA.SetTrigger("IsCaught");
        ChangeFace(eyesSurprise);
    }

    void ChangeFace(Vector2 newFace){
        Material targetMaterial = rend.materials[0];
        targetMaterial.mainTextureOffset = newFace;
    }
}