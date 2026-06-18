import { Composition } from "remotion";
import { BRTVideo3D } from "./BRTVideo3D";
import { SiliconTaiwanVideo } from "./SiliconTaiwanVideo";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="BRTVideo"
        component={BRTVideo3D}
        durationInFrames={7800} /* 4 minutes 20 seconds */
        fps={30}
        width={1920} /* YouTube standard horizontal */
        height={1080}
      />
      <Composition
        id="SiliconTaiwan"
        component={SiliconTaiwanVideo}
        durationInFrames={1800} /* 60 seconds (Videoclip) */
        fps={30}
        width={1920} /* Full HD standard */
        height={1080}
      />
    </>
  );
};
