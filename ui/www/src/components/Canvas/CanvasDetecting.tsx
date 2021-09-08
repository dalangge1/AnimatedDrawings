import React, { useEffect, useState } from "react";
import { Spinner } from "react-bootstrap";
import useDrawingStore from "../../hooks/useDrawingStore";
import { useDrawingApi } from "../../hooks/useDrawingApi";

import PoseEditor, { Position } from "../PoseEditor";
import Loader from "../Loader";

const mapJointsToPose = (joints: object) => {
  return {
    nodes: Object.entries(joints).map((arr) => {
      return { id: arr[0], label: arr[0], position: arr[1] as Position };
    }),
    edges: [
      // Right side
      {
        from: "right_shoulder",
        to: "right_elbow",
      },
      {
        from: "right_elbow",
        to: "right_wrist",
      },
      {
        from: "right_shoulder",
        to: "right_hip",
      },
      {
        from: "right_hip",
        to: "right_knee",
      },
      {
        from: "right_knee",
        to: "right_ankle",
      },
      // Left side
      {
        from: "left_shoulder",
        to: "left_elbow",
      },
      {
        from: "left_elbow",
        to: "left_wrist",
      },
      {
        from: "left_shoulder",
        to: "left_hip",
      },
      {
        from: "left_hip",
        to: "left_knee",
      },
      {
        from: "left_knee",
        to: "left_ankle",
      },
      // Shoulders and hips
      {
        from: "left_shoulder",
        to: "right_shoulder",
      },
      {
        from: "left_hip",
        to: "right_hip",
      },
      // face
      {
        from: "nose",
        to: "left_eye",
      },
      {
        from: "nose",
        to: "right_eye",
      },
      {
        from: "nose",
        to: "left_ear",
      },
      {
        from: "nose",
        to: "right_ear",
      },
      {
        from: "nose",
        to: "left_shoulder",
      },
      {
        from: "nose",
        to: "right_shoulder",
      },
    ],
  };
};

const CanvasUpload = () => {
  const {
    drawing,
    newCompressedDrawing,
    uuid,
    setUuid,
    pose,
    setPose,
  } = useDrawingStore();

  const {
    isLoading,
    uploadImage,
    getJointLocations,
    getCroppedImage,
  } = useDrawingApi((err) => {});

  const [imageUrl, setImageUrl] = useState<any>();

  /**
   * Here there are two scenarios/side effects when the CanvasDetecting component mounts
   * 1. Invokes API to uploadImage when not uuid is detected from the user, and fetch a new uuid.
   * 2. When an uuid is detected, invoke API to fetch a croppedImage with pose anotations.
   * The component will only rerender when the uuid dependency changes.
   * exhaustive-deps eslint warning was diable as no more dependencies are really necesary as side effects.
   * Contrary to this, including other function dependencies will trigger infinite loop rendereing.
   */
  useEffect(() => {
    const fetchUuid = async () => {
      try {
        await uploadImage(newCompressedDrawing, (data) =>
          setUuid(data as string)
        );
      } catch (error) {
        console.log(error);
      }
    };
    const fetchPose = async () => {
      try {
        await getCroppedImage(uuid!, (data) => {
          let reader = new window.FileReader();
          reader.readAsDataURL(data);
          reader.onload = function () {
            let imageDataUrl = reader.result;
            setImageUrl(imageDataUrl);
          };
        });

        getJointLocations(uuid!, (data) => {
          const mappedPose = mapJointsToPose(data);
          setPose(mappedPose);
        });
      } catch (error) {
        console.log(error);
      }
    };

    if (uuid === "") fetchUuid();
    if (uuid !== "") fetchPose();

    return () => {};
  }, [uuid]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="canvas-wrapper">
      <div className="canvas-background border border-dark">
        {isLoading ? (
          <Loader drawingURL={drawing} />
        ) : (
          <>
            {pose && (
              <PoseEditor imageUrl={imageUrl} pose={pose} setPose={setPose} />
            )}
          </>
        )}
      </div>

      <div className="mt-3">
        <button className="large-button border border-dark">
          {isLoading ? (
            <Spinner
              as="span"
              animation="border"
              size="sm"
              role="status"
              aria-hidden="true"
            />
          ) : (
            "Detected"
          )}
        </button>
      </div>
    </div>
  );
};

export default CanvasUpload;