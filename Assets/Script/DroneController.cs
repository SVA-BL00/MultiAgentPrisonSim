using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class DroneController : MonoBehaviour
{
    Rigidbody DR;
    public GameState gs;
    public CameraDetector detector;
    public List<GameObject> cameras;
    public float fixedDistance = 0.0001f;
    public float actionDuration = 0.1f;
    public float moveSpeed = 0.1f;
    public float rotationSpeed = 90f;
    private Quaternion targetRotation;
    private Vector3 targetPosition;
    public string whatTouched;
    private string currentAction = null;
    public string isPrisonerInView = "0";
    string[] cam = new string[] { "0", "0", "0", "0" };
    private Coroutine detectionCoroutine;

    void Awake()
    {
        DR = GetComponent<Rigidbody>();
    }

    void Start()
    {
        StartCoroutine(ActionCheck());
    }

    void Update()
    {
        if (detector.isDetected)
        {
            isPrisonerInView = "Prisoner";
        }
        if (currentAction != null)
        {
            if (currentAction == "move")
            {
                transform.position = Vector3.MoveTowards(transform.position, targetPosition, moveSpeed * Time.deltaTime);
                if (transform.position == targetPosition)
                {
                    currentAction = null;
                }
            }
            else if (currentAction.StartsWith("turn"))
            {
                transform.rotation = targetRotation;
                if (transform.rotation == targetRotation)
                {
                    currentAction = null;
                }
            }
        }
    }

    public void ActionHandler(string command)
    {
        currentAction = command;

        switch (command)
        {
            case "move":
                Vector3 newPosition = DR.transform.position - transform.forward * 10f;
                targetPosition = newPosition;
                break;

            case "turnN":
                Quaternion turnNorth = Quaternion.Euler(0, 0, 0);
                targetRotation = turnNorth;
                break;

            case "turnS":
                Quaternion turnSouth = Quaternion.Euler(0, 180, 0);
                targetRotation = turnSouth;
                break;

            case "turnE":
                Quaternion turnEast = Quaternion.Euler(0, 90, 0);
                targetRotation = turnEast;
                break;

            case "turnW":
                Quaternion turnWest = Quaternion.Euler(0, 270, 0);
                targetRotation = turnWest;
                break;

            case "idle":
                DR.velocity = Vector3.zero;
                DR.angularVelocity = Vector3.zero;
                targetPosition = transform.position;
                targetRotation = transform.rotation;
                break;

            case "move_forward":
                Vector3 newPositionF = DR.transform.position - transform.forward * 10f;
                targetPosition = newPositionF;
                break;

            case "move_down":
                targetPosition = new Vector3(
                    DR.transform.position.x,
                    DR.transform.position.y - 10f,
                    DR.transform.position.z
                );
                Debug.Log($"Move Down: Setting target position to {targetPosition}");
                break;

            default:
                Debug.Log("Unknown command received: " + command);
                break;
        }
    }

    void SendEnvironment()
    {
        for (int i = 0; i < cameras.Count; i++)
        {
            if (cameras[i].GetComponent<CameraDetector>().isDetected)
            {
                cam[i] = i.ToString();
            }
        }
        Vector3 position = DR.transform.position;
        string environmentData = $"{{\"position\": \"{position}\", " +
                                 $"\"cv\": \"{isPrisonerInView}\", " +
                                 $"\"Camera1\": \"{cam[0]}\", " +
                                 $"\"Camera2\": \"{cam[1]}\", " +
                                 $"\"Camera3\": \"{cam[2]}\", " +
                                 $"\"Camera4\": \"{cam[3]}\"}}";
        FindObjectOfType<Client>().socket.Emit("drone_handler", environmentData);
    }

    IEnumerator ActionCheck()
    {
        while (true)
        {
            SendEnvironment();
            yield return new WaitForSeconds(0.3f);
        }
    }

    void OnCollisionEnter(Collision collision)
    {
        DR.isKinematic = true;
        if (detectionCoroutine == null)
        {
            detectionCoroutine = StartCoroutine(DetectAndEndGame());
        }
    }

    IEnumerator DetectAndEndGame()
    {
        yield return new WaitForSeconds(3f);
        gs.EndGame();
    }
}
