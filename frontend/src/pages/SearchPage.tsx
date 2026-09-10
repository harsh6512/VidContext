import { Input } from "@/components/ui/input";
import { FaCircleArrowUp } from "react-icons/fa6";
import { CiPlay1 } from "react-icons/ci";
import { Card } from "@/components/ui/card";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import toast from "react-hot-toast";
import { useGlobalContext, type video } from "@/context/GlobalContext";
import { extractYoutubeVideoId } from "@/lib/utils";
import { Trash2, Loader2 } from "lucide-react";

function SearchPage() {
  const [input, setInput] = useState<string>("");
  const [videos, setVideos] = useState<video[]>([]);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const { authUser } = useGlobalContext();
  const navigate = useNavigate();

  const handleSubmit = async() => {
    const videoId = extractYoutubeVideoId(input);
    if(!videoId) {
      toast.error("Enter a valid youtube url");
      return;
    }

    navigate(`/learn/${videoId}`);
  }


  useEffect(()=> {
    const fetchAllvideos = async() => {
      try {
        const res = await fetch(`${import.meta.env.VITE_BACKEND_URI}/api/video/getAllVideos`,{
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + authUser?.token,
          }
        })
        const data = await res.json();
        if(data.error) {
          throw new Error(data.error);
        }
        setVideos(data);
      }
      catch(error) {
        if(error instanceof Error) {
          toast.error(error.message)
        }
      }
    }
    fetchAllvideos();
  },[authUser?.token])

  const handleDeleteVideo = async (e: React.MouseEvent, videoId: string) => {
    e.stopPropagation();
    if (deletingId) return;

    setDeletingId(videoId);
    try {
      const res = await fetch(`${import.meta.env.VITE_BACKEND_URI}/api/video/deleteVideo/${videoId}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer " + authUser?.token,
        }
      });

      const data = await res.json();
      if (!res.ok || data.error) {
        throw new Error(data.error || "Failed to remove video");
      }

      setVideos((prev) => prev.filter((v) => v._id !== videoId));
      toast.success("Video removed from recents");
    } catch (error) {
      if (error instanceof Error) {
        toast.error(error.message);
      } else {
        toast.error("Failed to remove video");
      }
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="bg-white/50 dark:bg-[#171717] h-full dark:text-white">
      <div className="flex flex-col justify-center items-center gap-8 h-80">
        <p className="font-semibold text-4xl">What do you want to learn?</p>
        <div className="w-[35rem] relative">
          <Input 
          type="url" 
          placeholder="Paste your link" 
          className="h-11" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          />
          <FaCircleArrowUp 
          className="size-7 absolute top-[0.5rem] right-4 text-[#8A8A8A] cursor-pointer"
          onClick={handleSubmit} 
          />
        </div>
      </div>

      {/* Recents */}
      <div className="flex flex-col gap-4 pb-10">
        <div className="text-xl font-semibold">Recents</div>
        {/* Cards */}
        {videos.length === 0 ? (
          <div className="text-sm text-neutral-500 dark:text-neutral-400">
            No recent videos yet. Paste a link above to get started!
          </div>
        ) : (
          <div className="flex gap-5 flex-wrap">
            {
              videos.map((v: video, indx)=> {
                const v_id = extractYoutubeVideoId(v.video_url) || "";
                return (
                  <Card 
                    key={v._id || indx}
                    onClick={()=> navigate(`/learn/${v_id}`)}
                    className="relative group w-[17rem] h-[14.5rem] cursor-pointer rounded-2xl pt-0 overflow-hidden shrink-0 transition-all hover:shadow-lg border border-neutral-200 dark:border-neutral-800"
                  >
                    <div className="relative w-full h-[10.5rem] overflow-hidden bg-neutral-100 dark:bg-neutral-900">
                      <img 
                        src={`https://img.youtube.com/vi/${v_id}/maxresdefault.jpg`} 
                        alt={v.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                        onError={(e) => {
                          (e.target as HTMLImageElement).src = `https://img.youtube.com/vi/${v_id}/hqdefault.jpg`;
                        }}
                      />
                      {/* Delete / Remove Button */}
                      <button
                        type="button"
                        title="Remove from recents"
                        aria-label="Remove from recents"
                        onClick={(e) => handleDeleteVideo(e, v._id)}
                        disabled={deletingId === v._id}
                        className="absolute top-2 right-2 p-1.5 rounded-full bg-black/60 hover:bg-red-600 text-white/80 hover:text-white backdrop-blur-md opacity-0 group-hover:opacity-100 transition-all duration-200 hover:scale-110 disabled:opacity-50 z-10 shadow-sm"
                      >
                        {deletingId === v._id ? (
                          <Loader2 className="size-4 animate-spin text-white" />
                        ) : (
                          <Trash2 className="size-4" />
                        )}
                      </button>
                    </div>
                    <div className="flex items-center gap-2 px-4 py-2">
                      <CiPlay1 className="shrink-0 text-neutral-500"/>
                      <div className="font-normal w-full truncate text-sm">{v.title}</div>
                    </div>
                  </Card>
                )
              })
            }
          </div>
        )}

      </div>
    </div>
  );
}

export default SearchPage;

