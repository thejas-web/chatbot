import { useState } from "react";
import { useNavigate } from "react-router-dom";

//const API_URL = "http://localhost:8000";
const API_URL = "";

function Login() {

    const navigate = useNavigate();

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");


    // ==================================================
    // LOGIN
    // ==================================================

    const handleLogin = async (event) => {

        event.preventDefault();

        setError("");

        if (!username.trim() || !password) {
            setError("Please enter username and password.");
            return;
        }

        try {

            setLoading(true);

            const response = await fetch(
                `${API_URL}/api/login`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json",
                    },

                    body: JSON.stringify({
                        username: username.trim(),
                        password: password,
                    }),
                }
            );


            // ------------------------------------------
            // LOGIN FAILED
            // ------------------------------------------

            if (!response.ok) {

                let message =
                    "Invalid username or password.";

                try {

                    const data =
                        await response.json();

                    if (data.detail) {
                        message = data.detail;
                    }

                } catch {
                    // Ignore JSON parsing error
                }

                throw new Error(message);
            }


            // ------------------------------------------
            // LOGIN SUCCESS
            // ------------------------------------------

            const data =
                await response.json();

            console.log(
                "Login successful"
            );


            // ------------------------------------------
            // STORE JWT
            // ------------------------------------------

            localStorage.setItem(
                "admin_access_token",
                data.access_token
            );


            // ------------------------------------------
            // GO TO ADMIN PANEL
            // ------------------------------------------

            navigate("/admin");

        } catch (err) {

            console.error(
                "Login failed:",
                err
            );

            setError(
                err.message ||
                "Login failed. Please try again."
            );

        } finally {

            setLoading(false);
        }
    };


    // ==================================================
    // UI
    // ==================================================

    return (

        <div style={styles.page}>

            <div style={styles.loginCard}>

                {/* ---------------------------------- */}
                {/* BRAND */}
                {/* ---------------------------------- */}

                <div style={styles.brand}>

                    <div style={styles.brandIcon}>
                        W
                    </div>

                    <div>

                        <div style={styles.brandTitle}>
                            Webenza
                        </div>

                        <div style={styles.brandSubtitle}>
                            AI Admin
                        </div>

                    </div>

                </div>


                {/* ---------------------------------- */}
                {/* HEADER */}
                {/* ---------------------------------- */}

                <div style={styles.header}>

                    <h1 style={styles.title}>
                        Admin Login
                    </h1>

                    <p style={styles.subtitle}>
                        Sign in to access the administration panel.
                    </p>

                </div>


                {/* ---------------------------------- */}
                {/* ERROR */}
                {/* ---------------------------------- */}

                {error && (

                    <div style={styles.errorBox}>
                        {error}
                    </div>

                )}


                {/* ---------------------------------- */}
                {/* FORM */}
                {/* ---------------------------------- */}

                <form onSubmit={handleLogin}>

                    {/* USERNAME */}

                    <div style={styles.field}>

                        <label style={styles.label}>
                            Username
                        </label>

                        <input
                            type="text"
                            value={username}
                            onChange={(event) =>
                                setUsername(
                                    event.target.value
                                )
                            }
                            placeholder="Enter username"
                            autoComplete="username"
                            style={styles.input}
                            disabled={loading}
                        />

                    </div>


                    {/* PASSWORD */}

                    <div style={styles.field}>

                        <label style={styles.label}>
                            Password
                        </label>

                        <input
                            type="password"
                            value={password}
                            onChange={(event) =>
                                setPassword(
                                    event.target.value
                                )
                            }
                            placeholder="Enter password"
                            autoComplete="current-password"
                            style={styles.input}
                            disabled={loading}
                        />

                    </div>


                    {/* LOGIN BUTTON */}

                    <button
                        type="submit"
                        disabled={loading}
                        style={
                            loading
                                ? styles.loginButtonDisabled
                                : styles.loginButton
                        }
                    >

                        {loading
                            ? "Signing in..."
                            : "Sign in"
                        }

                    </button>

                </form>

            </div>

        </div>
    );
}


// ==================================================
// STYLES
// ==================================================

const styles = {

    page: {
        minHeight: "100vh",
        background: "#f5f6f8",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "20px",
        boxSizing: "border-box",
        fontFamily:
            "Inter, system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
    },

    loginCard: {
        width: "100%",
        maxWidth: "400px",
        background: "#ffffff",
        border: "1px solid #e5e7eb",
        borderRadius: "10px",
        padding: "32px",
        boxSizing: "border-box",
        boxShadow:
            "0 10px 30px rgba(0,0,0,0.06)",
    },

    brand: {
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: "10px",
        marginBottom: "30px",
    },

    brandIcon: {
        width: "36px",
        height: "36px",
        borderRadius: "6px",
        background: "#1f2937",
        color: "#ffffff",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontWeight: 700,
        fontSize: "17px",
    },

    brandTitle: {
        fontSize: "16px",
        fontWeight: 600,
        color: "#111827",
    },

    brandSubtitle: {
        fontSize: "11px",
        color: "#9ca3af",
        marginTop: "2px",
    },

    header: {
        marginBottom: "24px",
    },

    title: {
        margin: 0,
        fontSize: "22px",
        fontWeight: 600,
        color: "#111827",
        textAlign: "center",
    },

    subtitle: {
        margin: "7px 0 0",
        fontSize: "12px",
        color: "#6b7280",
        textAlign: "center",
        lineHeight: "1.5",
    },

    errorBox: {
        background: "#fef2f2",
        border: "1px solid #fecaca",
        color: "#b91c1c",
        borderRadius: "6px",
        padding: "10px 12px",
        marginBottom: "18px",
        fontSize: "12px",
    },

    field: {
        marginBottom: "17px",
    },

    label: {
        display: "block",
        marginBottom: "6px",
        fontSize: "12px",
        fontWeight: 500,
        color: "#374151",
    },

    input: {
        width: "100%",
        boxSizing: "border-box",
        border: "1px solid #d1d5db",
        borderRadius: "6px",
        padding: "10px 11px",
        fontSize: "13px",
        color: "#111827",
        outline: "none",
        background: "#ffffff",
    },

    loginButton: {
        width: "100%",
        border: "none",
        borderRadius: "6px",
        padding: "11px",
        background: "#1f2937",
        color: "#ffffff",
        fontSize: "13px",
        fontWeight: 500,
        cursor: "pointer",
        marginTop: "5px",
    },

    loginButtonDisabled: {
        width: "100%",
        border: "none",
        borderRadius: "6px",
        padding: "11px",
        background: "#9ca3af",
        color: "#ffffff",
        fontSize: "13px",
        fontWeight: 500,
        cursor: "not-allowed",
        marginTop: "5px",
    },
};


export default Login;