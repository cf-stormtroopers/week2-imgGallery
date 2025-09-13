import React from "react";
import { useDownloadImageImagesDownloadImageFilenameGet } from "../api/generated";
import { AXIOS_INSTANCE, convertUrlToAbsolute } from "../api/axios";

interface ThumbnailProps {
  filename: string;
  alt?: string;
  size?: "small" | "medium" | "large";
  className?: string;
  style?: React.CSSProperties;
  lazy?: boolean;
}

const sizeMap = {
  small: 128,
  medium: 512,
  large: 1024,
};

export const Thumbnail: React.FC<ThumbnailProps> = ({
  filename,
  alt = "",
  size = "medium",
  className = "",
  style = {},
  lazy = true,
}) => {
  return (
    <img
      src={convertUrlToAbsolute("/images/download/" + filename)}
      alt={alt}
      width={sizeMap[size]}
      height={sizeMap[size]}
      loading={lazy ? "lazy" : undefined}
      className={`object-cover rounded ${className}`}
      style={style}
    />
  );
};

export default Thumbnail;
