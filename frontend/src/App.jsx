import {
    BrowserRouter,
    Routes,
    Route,
    Navigate,
} from "react-router-dom";

import AvatarWidget from "./AvatarWidget";
import AdminPanel from "./AdminPanel";
import Login from "./Login";


// ==================================================
// PROTECTED ADMIN ROUTE
// ==================================================

function ProtectedAdminRoute() {

    const token =
        localStorage.getItem(
            "admin_access_token"
        );

    // No login token → go to login page
    if (!token) {

        return (
            <Navigate
                to="/login"
                replace
            />
        );
    }

    // Token exists → allow admin panel
    return <AdminPanel />;
}


// ==================================================
// APP
// ==================================================

function App() {

    return (

        <BrowserRouter>

            <Routes>

                {/* ================================== */}
                {/* PUBLIC AVATAR */}
                {/* ================================== */}

                <Route
                    path="/"
                    element={
                        <AvatarWidget />
                    }
                />


                {/* ================================== */}
                {/* ADMIN LOGIN */}
                {/* ================================== */}

                <Route
                    path="/login"
                    element={
                        <Login />
                    }
                />


                {/* ================================== */}
                {/* PROTECTED ADMIN */}
                {/* ================================== */}

                <Route
                    path="/admin"
                    element={
                        <ProtectedAdminRoute />
                    }
                />


                {/* ================================== */}
                {/* UNKNOWN URL */}
                {/* ================================== */}

                <Route
                    path="*"
                    element={
                        <Navigate
                            to="/"
                            replace
                        />
                    }
                />

            </Routes>

        </BrowserRouter>
    );
}


export default App;