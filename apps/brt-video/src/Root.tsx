import { Composition } from "remotion";
import { BRTVideo3D } from "./BRTVideo3D";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="BRTVideo"
        component={BRTVideo3D}
        durationInFrames={300}
        fps={30}
        width={1080}
        height={1920}
      />
    </>
  );
};
