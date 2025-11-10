import { useState, useEffect } from "react";

function CountdownTimer({ minutes = 5, onTimeout, onSuccess, success }) {
    const [timeLeft, setTimeLeft] = useState(minutes * 60); // giây

    useEffect(() => {
        if (timeLeft <= 0) {
            onTimeout?.(); // gọi callback khi hết giờ
            return;
        }
        if (success) {
            onSuccess?.();   // gọi callback hiển thị nút
            return;          // dừng bộ đếm
        }

        const interval = setInterval(() => {
            setTimeLeft(prev => prev - 1);
        }, 1000);

        return () => clearInterval(interval); // cleanup
    }, [timeLeft, onTimeout, onSuccess, success]);

    // format mm:ss
    const formatTime = (seconds) => {
        const m = String(Math.floor(seconds / 60)).padStart(2, "0");
        const s = String(seconds % 60).padStart(2, "0");
        return `${m}:${s}`;
    };

    return (
        <>
            <div className="text-center font-bold text-red-600 text-xl">
                <span className="animate-wiggle ">⏳</span> Thời gian còn lại: {formatTime(timeLeft)}
            </div>
        </>
    );
}

export default CountdownTimer;