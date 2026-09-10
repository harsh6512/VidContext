import logo from "@/assets/you_logo.png";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { useRef } from "react";
import { Link, useNavigate } from "react-router";
import { useGlobalContext } from "@/context/GlobalContext";

gsap.registerPlugin(useGSAP);

function Navbar() {
  const logoref = useRef<HTMLDivElement | null>(null);
  const navtagsref = useRef<HTMLDivElement | null>(null);
  const navbuttonref = useRef<HTMLDivElement | null>(null);
  const { authUser, setAuthUser, selectedVideo,setSelectedVideo,setChatMessages } = useGlobalContext();
  const navigate = useNavigate();

  const handleAuth = () => {
    if (authUser) {
      localStorage.removeItem("you-user");
      setAuthUser(null);
      setSelectedVideo(null);
      setChatMessages([]);
      navigate("/");
    } else {
      navigate("/signup");
    }
  };

  useGSAP(() => {
    const elements = [logoref.current, navtagsref.current, navbuttonref.current].filter(Boolean);
    gsap.from(elements, {
      y: -50,
      duration: 0.6,
      opacity: 0,
      stagger: 0.2,
    });
  });

  return (
    <nav className="flex backdrop-blur-lg bg-white/50 pb-4 pt-4 border-b border-[#F6F6F6] fixed top-0 w-full z-10 font-roboto">
      <Link to={authUser ? "/learn" : "/"}>
        <div className="ml-28 flex gap-2 cursor-pointer items-center" ref={logoref}>
          <img src={logo} alt="logo" className="w-8 h-8 mix-blend-multiply" />
          <div className="font-bold tracking-wide">{!selectedVideo && "VidContext"}</div>
        </div>
      </Link>

      {selectedVideo && (
        <div
          className="flex text-gray-900 ml-4 items-center font-roboto"
          ref={navtagsref}
        >
          {selectedVideo.title}
        </div>
      )}

      <div
        className="ml-auto mr-28 bg-black py-1.5 px-4 rounded-full"
        ref={navbuttonref}
      >
        <button className="text-white cursor-pointer" onClick={handleAuth}>
          {authUser ? "Sign out" : "Get Started"}
        </button>
      </div>
    </nav>
  );
}

export default Navbar;
