import { Composition } from "remotion";
import { BRTVideo } from "./BRTVideo";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="BRTVideo"
        component={BRTVideo}
        durationInFrames={300}
        fps={30}
        width={1080}
        height={1920}
      />
    </>
  );
};
