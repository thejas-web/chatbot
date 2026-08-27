import { useEffect, useState } from "react";

//const API_URL = "http://localhost:8000";
const API_URL = "";

const PAGE_SIZE_OPTIONS = [10, 20, 50];

function AdminPanel() {

    // ==================================================
    // ACTIVE SECTION
    // ==================================================

    const [activeSection, setActiveSection] =
        useState("dashboard");


    // ==================================================
    // DASHBOARD STATE
    // ==================================================

    const [dashboardStats, setDashboardStats] = useState({
        leads: 0,
        sessions: 0,
        messages: 0,
    });

    const [dashboardLoading, setDashboardLoading] =
        useState(false);


    // ==================================================
    // LEADS STATE
    // ==================================================

    const [leads, setLeads] =
        useState([]);

    const [leadPage, setLeadPage] =
        useState(1);

    const [leadPageSize, setLeadPageSize] =
        useState(20);

    const [leadTotal, setLeadTotal] =
        useState(0);

    const [leadTotalPages, setLeadTotalPages] =
        useState(0);


    // ==================================================
    // SESSIONS STATE
    // ==================================================

    const [sessions, setSessions] =
        useState([]);

    const [sessionPage, setSessionPage] =
        useState(1);

    const [sessionPageSize, setSessionPageSize] =
        useState(20);

    const [sessionTotal, setSessionTotal] =
        useState(0);

    const [sessionTotalPages, setSessionTotalPages] =
        useState(0);


    // ==================================================
    // MESSAGES STATE
    // ==================================================

    const [messages, setMessages] =
        useState([]);

    const [messagePage, setMessagePage] =
        useState(1);

    const [messagePageSize, setMessagePageSize] =
        useState(20);

    const [messageTotal, setMessageTotal] =
        useState(0);

    const [messageTotalPages, setMessageTotalPages] =
        useState(0);


    // ==================================================
    // GENERAL STATE
    // ==================================================

    const [loading, setLoading] =
        useState(false);

    const [error, setError] =
        useState("");


    // ==================================================
    // SELECTED DETAILS
    // ==================================================

    const [selectedLead, setSelectedLead] =
        useState(null);

    const [selectedSession, setSelectedSession] =
        useState(null);

    const [selectedMessage, setSelectedMessage] =
        useState(null);


    // ==================================================
    // FETCH DASHBOARD STATISTICS
    // ==================================================

    const fetchDashboardStats = async () => {

        try {

            setDashboardLoading(true);

            const [
                leadsResponse,
                sessionsResponse,
                messagesResponse,
            ] = await Promise.all([

                fetch(
                    `${API_URL}/api/leads?page=1&page_size=1`
                ),

                fetch(
                    `${API_URL}/api/sessions?page=1&page_size=1`
                ),

                fetch(
                    `${API_URL}/api/messages?page=1&page_size=1`
                ),

            ]);


            if (!leadsResponse.ok) {
                throw new Error(
                    "Failed to fetch lead statistics."
                );
            }

            if (!sessionsResponse.ok) {
                throw new Error(
                    "Failed to fetch session statistics."
                );
            }

            if (!messagesResponse.ok) {
                throw new Error(
                    "Failed to fetch message statistics."
                );
            }


            const leadsData =
                await leadsResponse.json();

            const sessionsData =
                await sessionsResponse.json();

            const messagesData =
                await messagesResponse.json();


            setDashboardStats({

                leads:
                    leadsData.total || 0,

                sessions:
                    sessionsData.total || 0,

                messages:
                    messagesData.total || 0,

            });

        } catch (err) {

            console.error(
                "Failed to fetch dashboard statistics:",
                err
            );

        } finally {

            setDashboardLoading(false);

        }
    };


    // ==================================================
    // FETCH LEADS
    // ==================================================

    const fetchLeads = async () => {

        try {

            setLoading(true);
            setError("");

            const response = await fetch(
                `${API_URL}/api/leads?page=${leadPage}&page_size=${leadPageSize}`
            );


            if (!response.ok) {

                const errorText =
                    await response.text();

                throw new Error(
                    `Failed to fetch leads: ${errorText}`
                );
            }


            const data =
                await response.json();


            console.log(
                "Admin leads response:",
                data
            );


            setLeads(
                data.items || []
            );

            setLeadTotal(
                data.total || 0
            );

            setLeadTotalPages(
                data.total_pages || 0
            );

        } catch (err) {

            console.error(
                "Failed to fetch leads:",
                err
            );

            setError(
                err?.message ||
                "Failed to load leads."
            );

        } finally {

            setLoading(false);

        }
    };


    // ==================================================
    // FETCH SESSIONS
    // ==================================================

    const fetchSessions = async () => {

        try {

            setLoading(true);
            setError("");

            const response = await fetch(
                `${API_URL}/api/sessions?page=${sessionPage}&page_size=${sessionPageSize}`
            );


            if (!response.ok) {

                const errorText =
                    await response.text();

                throw new Error(
                    `Failed to fetch sessions: ${errorText}`
                );
            }


            const data =
                await response.json();


            console.log(
                "Admin sessions response:",
                data
            );


            setSessions(
                data.items || []
            );

            setSessionTotal(
                data.total || 0
            );

            setSessionTotalPages(
                data.total_pages || 0
            );

        } catch (err) {

            console.error(
                "Failed to fetch sessions:",
                err
            );

            setError(
                err?.message ||
                "Failed to load sessions."
            );

        } finally {

            setLoading(false);

        }
    };


    // ==================================================
    // FETCH MESSAGES
    // ==================================================

    const fetchMessages = async () => {

        try {

            setLoading(true);
            setError("");

            const response = await fetch(
                `${API_URL}/api/messages?page=${messagePage}&page_size=${messagePageSize}`
            );


            if (!response.ok) {

                const errorText =
                    await response.text();

                throw new Error(
                    `Failed to fetch messages: ${errorText}`
                );
            }


            const data =
                await response.json();


            console.log(
                "Admin messages response:",
                data
            );


            setMessages(
                data.items || []
            );

            setMessageTotal(
                data.total || 0
            );

            setMessageTotalPages(
                data.total_pages || 0
            );

        } catch (err) {

            console.error(
                "Failed to fetch messages:",
                err
            );

            setError(
                err?.message ||
                "Failed to load messages."
            );

        } finally {

            setLoading(false);

        }
    };


    // ==================================================
    // INITIAL DASHBOARD LOAD
    // ==================================================

    useEffect(() => {

        fetchDashboardStats();

    }, []);


    // ==================================================
    // LOAD ACTIVE SECTION
    // ==================================================

    useEffect(() => {

        setError("");

        if (activeSection === "leads") {
            fetchLeads();
        }

        if (activeSection === "sessions") {
            fetchSessions();
        }

        if (activeSection === "messages") {
            fetchMessages();
        }

    }, [
        activeSection,

        leadPage,
        leadPageSize,

        sessionPage,
        sessionPageSize,

        messagePage,
        messagePageSize,
    ]);


    // ==================================================
    // PAGE NUMBERS
    // ==================================================

    const getPageNumbers = (totalPages) => {

        const pages = [];

        for (
            let i = 1;
            i <= totalPages;
            i++
        ) {

            pages.push(i);

        }

        return pages;
    };


    // ==================================================
    // FORMAT DATE
    // ==================================================

    const formatDate = (date) => {

        if (!date) {
            return "-";
        }

        const parsedDate =
            new Date(date);

        if (isNaN(parsedDate.getTime())) {
            return "-";
        }

        return parsedDate.toLocaleString(
            "en-IN",
            {
                dateStyle: "medium",
                timeStyle: "short",
            }
        );
    };


    // ==================================================
    // DASHBOARD
    // ==================================================

    const renderDashboard = () => {

        return (
            <div>

                <div style={styles.contentHeader}>

                    <div>

                        <h1 style={styles.pageTitle}>
                            Dashboard
                        </h1>

                        <p style={styles.pageSubtitle}>
                            Webenza AI Assistant administration
                        </p>

                    </div>


                    <button
                        onClick={fetchDashboardStats}
                        style={styles.refreshButton}
                    >
                        ↻ Refresh
                    </button>

                </div>


                <div style={styles.dashboardGrid}>

                    {/* LEADS */}

                    <div style={styles.statCard}>

                        <div style={styles.statLabel}>
                            Total Leads
                        </div>

                        <div style={styles.statValue}>

                            {dashboardLoading
                                ? "..."
                                : dashboardStats.leads}

                        </div>

                    </div>


                    {/* SESSIONS */}

                    <div style={styles.statCard}>

                        <div style={styles.statLabel}>
                            Total Sessions
                        </div>

                        <div style={styles.statValue}>

                            {dashboardLoading
                                ? "..."
                                : dashboardStats.sessions}

                        </div>

                    </div>


                    {/* MESSAGES */}

                    <div style={styles.statCard}>

                        <div style={styles.statLabel}>
                            Total Messages
                        </div>

                        <div style={styles.statValue}>

                            {dashboardLoading
                                ? "..."
                                : dashboardStats.messages}

                        </div>

                    </div>

                </div>

            </div>
        );
    };


    // ==================================================
    // LEADS
    // ==================================================

    const renderLeads = () => {

        return (
            <div>

                <div style={styles.contentHeader}>

                    <div>

                        <h1 style={styles.pageTitle}>
                            Leads
                        </h1>

                        <p style={styles.pageSubtitle}>
                            Manage leads captured by the AI assistant
                        </p>

                    </div>


                    <div style={styles.totalBadge}>
                        {leadTotal} total
                    </div>

                </div>


                <div style={styles.toolbar}>

                    <div style={styles.toolbarLeft}>

                        <span style={styles.toolbarLabel}>
                            Show
                        </span>

                        <select
                            value={leadPageSize}
                            onChange={(event) => {

                                setLeadPageSize(
                                    Number(event.target.value)
                                );

                                setLeadPage(1);

                                setSelectedLead(null);

                            }}
                            style={styles.pageSizeSelect}
                        >

                            {PAGE_SIZE_OPTIONS.map(
                                (size) => (

                                    <option
                                        key={size}
                                        value={size}
                                    >
                                        {size}
                                    </option>

                                )
                            )}

                        </select>

                        <span style={styles.toolbarLabel}>
                            entries
                        </span>

                    </div>


                    <button
                        onClick={fetchLeads}
                        style={styles.refreshButton}
                    >
                        ↻ Refresh
                    </button>

                </div>


                {error && (

                    <div style={styles.errorBox}>
                        {error}
                    </div>

                )}


                <div style={styles.tableContainer}>

                    {loading ? (

                        <div style={styles.loading}>
                            Loading leads...
                        </div>

                    ) : leads.length === 0 ? (

                        <div style={styles.emptyState}>
                            No leads found.
                        </div>

                    ) : (

                        <table style={styles.table}>

                            <thead>

                                <tr>

                                    <th style={styles.th}>
                                        Name
                                    </th>

                                    <th style={styles.th}>
                                        Email
                                    </th>

                                    <th style={styles.th}>
                                        Phone
                                    </th>

                                    <th style={styles.th}>
                                        Status
                                    </th>

                                    <th style={styles.th}>
                                        Created
                                    </th>

                                </tr>

                            </thead>


                            <tbody>

                                {leads.map(
                                    (lead) => (

                                        <tr
                                            key={lead.id}
                                            onClick={() =>
                                                setSelectedLead(
                                                    lead
                                                )
                                            }
                                            style={
                                                styles.tableRow
                                            }
                                        >

                                            <td style={styles.td}>
                                                <span
                                                    style={
                                                        styles.nameCell
                                                    }
                                                >
                                                    {lead.name || "-"}
                                                </span>
                                            </td>

                                            <td style={styles.td}>
                                                {lead.email || "-"}
                                            </td>

                                            <td style={styles.td}>
                                                {lead.phone || "-"}
                                            </td>

                                            <td style={styles.td}>

                                                <span
                                                    style={
                                                        lead.status ===
                                                        "new"
                                                            ? styles.statusNew
                                                            : styles.statusDefault
                                                    }
                                                >
                                                    {lead.status || "-"}
                                                </span>

                                            </td>

                                            <td style={styles.td}>
                                                {formatDate(
                                                    lead.created_at
                                                )}
                                            </td>

                                        </tr>

                                    )
                                )}

                            </tbody>

                        </table>

                    )}

                </div>


                <Pagination
                    page={leadPage}
                    totalPages={leadTotalPages}
                    total={leadTotal}
                    pageSize={leadPageSize}
                    onPageChange={(newPage) => {
                        setLeadPage(newPage);
                        setSelectedLead(null);
                    }}
                />


                {selectedLead && (

                    <DetailPanel
                        title="Lead Details"
                        subtitle={selectedLead.name}
                        onClose={() =>
                            setSelectedLead(null)
                        }
                    >

                        <DetailRow
                            label="Name"
                            value={selectedLead.name}
                        />

                        <DetailRow
                            label="Email"
                            value={selectedLead.email}
                        />

                        <DetailRow
                            label="Phone"
                            value={selectedLead.phone}
                        />

                        <DetailRow
                            label="Status"
                            value={selectedLead.status}
                        />

                        <DetailRow
                            label="Session ID"
                            value={selectedLead.session_id}
                        />

                        <DetailRow
                            label="Lead ID"
                            value={selectedLead.id}
                        />

                        <DetailRow
                            label="Created At"
                            value={formatDate(
                                selectedLead.created_at
                            )}
                        />

                    </DetailPanel>

                )}

            </div>
        );
    };


    // ==================================================
    // SESSIONS
    // ==================================================

    const renderSessions = () => {

        return (
            <div>

                <div style={styles.contentHeader}>

                    <div>

                        <h1 style={styles.pageTitle}>
                            Sessions
                        </h1>

                        <p style={styles.pageSubtitle}>
                            View conversations started with the AI assistant
                        </p>

                    </div>


                    <div style={styles.totalBadge}>
                        {sessionTotal} total
                    </div>

                </div>


                <div style={styles.toolbar}>

                    <div style={styles.toolbarLeft}>

                        <span style={styles.toolbarLabel}>
                            Show
                        </span>

                        <select
                            value={sessionPageSize}
                            onChange={(event) => {

                                setSessionPageSize(
                                    Number(event.target.value)
                                );

                                setSessionPage(1);

                                setSelectedSession(null);

                            }}
                            style={styles.pageSizeSelect}
                        >

                            {PAGE_SIZE_OPTIONS.map(
                                (size) => (

                                    <option
                                        key={size}
                                        value={size}
                                    >
                                        {size}
                                    </option>

                                )
                            )}

                        </select>

                        <span style={styles.toolbarLabel}>
                            entries
                        </span>

                    </div>


                    <button
                        onClick={fetchSessions}
                        style={styles.refreshButton}
                    >
                        ↻ Refresh
                    </button>

                </div>


                {error && (

                    <div style={styles.errorBox}>
                        {error}
                    </div>

                )}


                <div style={styles.tableContainer}>

                    {loading ? (

                        <div style={styles.loading}>
                            Loading sessions...
                        </div>

                    ) : sessions.length === 0 ? (

                        <div style={styles.emptyState}>
                            No sessions found.
                        </div>

                    ) : (

                        <table style={styles.table}>

                            <thead>

                                <tr>

                                    <th style={styles.th}>
                                        Session ID
                                    </th>

                                    <th style={styles.th}>
                                        User Messages
                                    </th>

                                    <th style={styles.th}>
                                        Created
                                    </th>

                                </tr>

                            </thead>


                            <tbody>

                                {sessions.map(
                                    (session) => (

                                        <tr
                                            key={session.id}
                                            onClick={() =>
                                                setSelectedSession(
                                                    session
                                                )
                                            }
                                            style={
                                                styles.tableRow
                                            }
                                        >

                                            <td style={styles.td}>
                                                <span
                                                    style={
                                                        styles.nameCell
                                                    }
                                                >
                                                    {session.id || "-"}
                                                </span>
                                            </td>

                                            <td style={styles.td}>
                                                {
                                                    session.user_message_count ??
                                                    "-"
                                                }
                                            </td>

                                            <td style={styles.td}>
                                                {formatDate(
                                                    session.created_at
                                                )}
                                            </td>

                                        </tr>

                                    )
                                )}

                            </tbody>

                        </table>

                    )}

                </div>


                <Pagination
                    page={sessionPage}
                    totalPages={sessionTotalPages}
                    total={sessionTotal}
                    pageSize={sessionPageSize}
                    onPageChange={(newPage) => {
                        setSessionPage(newPage);
                        setSelectedSession(null);
                    }}
                />


                {selectedSession && (

                    <DetailPanel
                        title="Session Details"
                        subtitle={selectedSession.id}
                        onClose={() =>
                            setSelectedSession(null)
                        }
                    >

                        <DetailRow
                            label="Session ID"
                            value={selectedSession.id}
                        />

                        <DetailRow
                            label="User Messages"
                            value={
                                selectedSession.user_message_count
                            }
                        />

                        <DetailRow
                            label="Created At"
                            value={formatDate(
                                selectedSession.created_at
                            )}
                        />

                    </DetailPanel>

                )}

            </div>
        );
    };


    // ==================================================
    // MESSAGES
    // ==================================================

    const renderMessages = () => {

        return (
            <div>

                <div style={styles.contentHeader}>

                    <div>

                        <h1 style={styles.pageTitle}>
                            Messages
                        </h1>

                        <p style={styles.pageSubtitle}>
                            View messages exchanged with the AI assistant
                        </p>

                    </div>


                    <div style={styles.totalBadge}>
                        {messageTotal} total
                    </div>

                </div>


                <div style={styles.toolbar}>

                    <div style={styles.toolbarLeft}>

                        <span style={styles.toolbarLabel}>
                            Show
                        </span>

                        <select
                            value={messagePageSize}
                            onChange={(event) => {

                                setMessagePageSize(
                                    Number(event.target.value)
                                );

                                setMessagePage(1);

                                setSelectedMessage(null);

                            }}
                            style={styles.pageSizeSelect}
                        >

                            {PAGE_SIZE_OPTIONS.map(
                                (size) => (

                                    <option
                                        key={size}
                                        value={size}
                                    >
                                        {size}
                                    </option>

                                )
                            )}

                        </select>

                        <span style={styles.toolbarLabel}>
                            entries
                        </span>

                    </div>


                    <button
                        onClick={fetchMessages}
                        style={styles.refreshButton}
                    >
                        ↻ Refresh
                    </button>

                </div>


                {error && (

                    <div style={styles.errorBox}>
                        {error}
                    </div>

                )}


                <div style={styles.tableContainer}>

                    {loading ? (

                        <div style={styles.loading}>
                            Loading messages...
                        </div>

                    ) : messages.length === 0 ? (

                        <div style={styles.emptyState}>
                            No messages found.
                        </div>

                    ) : (

                        <table style={styles.table}>

                            <thead>

                                <tr>

                                    <th style={styles.th}>
                                        Session ID
                                    </th>

                                    <th style={styles.th}>
                                        Role
                                    </th>

                                    <th style={styles.th}>
                                        Message
                                    </th>

                                    <th style={styles.th}>
                                        Created
                                    </th>

                                </tr>

                            </thead>


                            <tbody>

                                {messages.map(
                                    (message) => (

                                        <tr
                                            key={message.id}
                                            onClick={() =>
                                                setSelectedMessage(
                                                    message
                                                )
                                            }
                                            style={
                                                styles.tableRow
                                            }
                                        >

                                            <td style={styles.td}>
                                                {message.session_id || "-"}
                                            </td>

                                            <td style={styles.td}>

                                                <span
                                                    style={
                                                        message.role ===
                                                        "user"
                                                            ? styles.roleUser
                                                            : styles.roleAssistant
                                                    }
                                                >
                                                    {message.role || "-"}
                                                </span>

                                            </td>

                                            <td
                                                style={{
                                                    ...styles.td,
                                                    maxWidth: "400px",
                                                    overflow: "hidden",
                                                    textOverflow:
                                                        "ellipsis",
                                                }}
                                            >
                                                {message.content || "-"}
                                            </td>

                                            <td style={styles.td}>
                                                {formatDate(
                                                    message.created_at
                                                )}
                                            </td>

                                        </tr>

                                    )
                                )}

                            </tbody>

                        </table>

                    )}

                </div>


                <Pagination
                    page={messagePage}
                    totalPages={messageTotalPages}
                    total={messageTotal}
                    pageSize={messagePageSize}
                    onPageChange={(newPage) => {
                        setMessagePage(newPage);
                        setSelectedMessage(null);
                    }}
                />


                {selectedMessage && (

                    <DetailPanel
                        title="Message Details"
                        subtitle={selectedMessage.role}
                        onClose={() =>
                            setSelectedMessage(null)
                        }
                    >

                        <DetailRow
                            label="Message ID"
                            value={selectedMessage.id}
                        />

                        <DetailRow
                            label="Session ID"
                            value={selectedMessage.session_id}
                        />

                        <DetailRow
                            label="Role"
                            value={selectedMessage.role}
                        />

                        <DetailRow
                            label="Message"
                            value={selectedMessage.content}
                        />

                        <DetailRow
                            label="Created At"
                            value={formatDate(
                                selectedMessage.created_at
                            )}
                        />

                    </DetailPanel>

                )}

            </div>
        );
    };


    // ==================================================
    // MAIN UI
    // ==================================================

    return (
        <div style={styles.adminLayout}>

            {/* ==========================================
                SIDEBAR
            ========================================== */}

            <aside style={styles.sidebar}>

                <div style={styles.sidebarBrand}>

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


                {/* MAIN */}

                <div style={styles.sidebarSection}>

                    <div style={styles.sidebarSectionTitle}>
                        MAIN
                    </div>


                    <button
                        onClick={() =>
                            setActiveSection("dashboard")
                        }
                        style={
                            activeSection === "dashboard"
                                ? styles.sidebarItemActive
                                : styles.sidebarItem
                        }
                    >

                        <span>
                            ▦
                        </span>

                        Dashboard

                    </button>

                </div>


                {/* LEADS */}

                <div style={styles.sidebarSection}>

                    <div style={styles.sidebarSectionTitle}>
                        LEADS
                    </div>


                    <button
                        onClick={() =>
                            setActiveSection("leads")
                        }
                        style={
                            activeSection === "leads"
                                ? styles.sidebarItemActive
                                : styles.sidebarItem
                        }
                    >

                        <span>
                            👤
                        </span>

                        Leads

                    </button>

                </div>


                {/* CHAT */}

                <div style={styles.sidebarSection}>

                    <div style={styles.sidebarSectionTitle}>
                        CHAT
                    </div>


                    <button
                        onClick={() =>
                            setActiveSection("sessions")
                        }
                        style={
                            activeSection === "sessions"
                                ? styles.sidebarItemActive
                                : styles.sidebarItem
                        }
                    >

                        <span>
                            💬
                        </span>

                        Sessions

                    </button>


                    <button
                        onClick={() =>
                            setActiveSection("messages")
                        }
                        style={
                            activeSection === "messages"
                                ? styles.sidebarItemActive
                                : styles.sidebarItem
                        }
                    >

                        <span>
                            📝
                        </span>

                        Messages

                    </button>

                </div>


                {/* ADMIN USER */}

                <div style={styles.sidebarBottom}>

                    <div style={styles.adminUser}>

                        <div style={styles.userAvatar}>
                            A
                        </div>

                        <div>

                            <div style={styles.userName}>
                                Administrator
                            </div>

                            <div style={styles.userRole}>
                                Admin
                            </div>

                        </div>

                    </div>


                    <button
                        onClick={() => {

                            localStorage.removeItem(
                                "admin_access_token"
                            );

                            window.location.href = "/login";

                        }}
                        style={styles.logoutButton}
                    >
                        Logout
                    </button>

                </div>

            </aside>


            {/* ==========================================
                MAIN CONTENT
            ========================================== */}

            <main style={styles.mainContent}>

                {/* TOP BAR */}

                <header style={styles.topBar}>

                    <div style={styles.breadcrumb}>

                        Admin

                        <span>
                            /
                        </span>

                        <strong>

                            {activeSection === "leads"
                                ? "Leads"
                                : activeSection === "sessions"
                                    ? "Sessions"
                                    : activeSection === "messages"
                                        ? "Messages"
                                        : "Dashboard"}

                        </strong>

                    </div>


                    <div style={styles.topBarRight}>

                        <button
                            style={styles.viewSiteButton}
                            onClick={() =>
                                window.open(
                                    "/",
                                    "_blank"
                                )
                            }
                        >
                            View site ↗
                        </button>

                    </div>

                </header>


                {/* CONTENT */}

                <div style={styles.content}>

                    {activeSection === "dashboard"
                        ? renderDashboard()
                        : activeSection === "leads"
                            ? renderLeads()
                            : activeSection === "sessions"
                                ? renderSessions()
                                : renderMessages()}

                </div>

            </main>

        </div>
    );
}


// ==================================================
// PAGINATION COMPONENT
// ==================================================

function Pagination({
    page,
    totalPages,
    total,
    pageSize,
    onPageChange,
}) {

    if (totalPages <= 0) {
        return null;
    }


    const pages = [];

    for (
        let i = 1;
        i <= totalPages;
        i++
    ) {
        pages.push(i);
    }


    return (

        <div style={styles.pagination}>

            <div style={styles.paginationInfo}>

                Showing{" "}

                <strong>
                    {(page - 1) * pageSize + 1}
                </strong>

                {" "}–{" "}

                <strong>
                    {Math.min(
                        page * pageSize,
                        total
                    )}
                </strong>

                {" "}of{" "}

                <strong>
                    {total}
                </strong>

            </div>


            <div style={styles.paginationControls}>

                <button
                    onClick={() =>
                        onPageChange(page - 1)
                    }
                    disabled={page === 1}
                    style={
                        page === 1
                            ? styles.paginationButtonDisabled
                            : styles.paginationButton
                    }
                >
                    ← Previous
                </button>


                {pages.map(
                    (pageNumber) => (

                        <button
                            key={pageNumber}
                            onClick={() =>
                                onPageChange(
                                    pageNumber
                                )
                            }
                            style={
                                pageNumber === page
                                    ? styles.paginationActive
                                    : styles.paginationButton
                            }
                        >
                            {pageNumber}
                        </button>

                    )
                )}


                <button
                    onClick={() =>
                        onPageChange(page + 1)
                    }
                    disabled={
                        page === totalPages
                    }
                    style={
                        page === totalPages
                            ? styles.paginationButtonDisabled
                            : styles.paginationButton
                    }
                >
                    Next →
                </button>

            </div>

        </div>
    );
}


// ==================================================
// DETAIL PANEL
// ==================================================

function DetailPanel({
    title,
    subtitle,
    onClose,
    children,
}) {

    return (

        <div style={styles.detailOverlay}>

            <div style={styles.detailPanel}>

                <div style={styles.detailHeader}>

                    <div>

                        <h2 style={styles.detailTitle}>
                            {title}
                        </h2>

                        <p style={styles.detailSubtitle}>
                            {subtitle || "-"}
                        </p>

                    </div>


                    <button
                        onClick={onClose}
                        style={styles.closeButton}
                    >
                        ×
                    </button>

                </div>


                <div style={styles.detailBody}>

                    {children}

                </div>

            </div>

        </div>
    );
}


// ==================================================
// DETAIL ROW
// ==================================================

function DetailRow({
    label,
    value,
}) {

    return (

        <div style={styles.detailRow}>

            <div style={styles.detailLabel}>
                {label}
            </div>

            <div style={styles.detailValue}>
                {value || "-"}
            </div>

        </div>
    );
}


// ==================================================
// STYLES
// ==================================================

const styles = {

    // ==============================================
    // LAYOUT
    // ==============================================

    adminLayout: {
        minHeight: "100vh",
        width: "100%",
        display: "flex",
        background: "#f5f6f8",
        fontFamily:
            "Inter, system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
        color: "#1f2937",
        boxSizing: "border-box",
    },

    
    logoutButton: {
        width: "100%",
        marginTop: "14px",
        border: "1px solid rgba(255,255,255,0.15)",
        background: "transparent",
        color: "#d1d5db",
        borderRadius: "6px",
        padding: "8px 10px",
        fontSize: "11px",
        cursor: "pointer",
        textAlign: "left",
    },


    // ==============================================
    // SIDEBAR
    // ==============================================

    sidebar: {
        width: "240px",
        minHeight: "100vh",
        background: "#1f2937",
        color: "#ffffff",
        display: "flex",
        flexDirection: "column",
        flexShrink: 0,
    },

    sidebarBrand: {
        height: "72px",
        display: "flex",
        alignItems: "center",
        gap: "12px",
        padding: "0 20px",
        borderBottom:
            "1px solid rgba(255,255,255,0.08)",
        boxSizing: "border-box",
    },

    brandIcon: {
        width: "34px",
        height: "34px",
        borderRadius: "6px",
        background: "#ffffff",
        color: "#1f2937",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontWeight: 700,
        fontSize: "17px",
        flexShrink: 0,
    },

    brandTitle: {
        fontSize: "15px",
        fontWeight: 600,
    },

    brandSubtitle: {
        fontSize: "11px",
        color: "#9ca3af",
        marginTop: "2px",
    },

    sidebarSection: {
        padding: "22px 12px 0",
    },

    sidebarSectionTitle: {
        fontSize: "10px",
        fontWeight: 700,
        color: "#9ca3af",
        letterSpacing: "0.08em",
        padding: "0 10px 8px",
    },

    sidebarItem: {
        width: "100%",
        border: "none",
        background: "transparent",
        color: "#d1d5db",
        padding: "10px",
        borderRadius: "6px",
        display: "flex",
        alignItems: "center",
        gap: "10px",
        fontSize: "13px",
        textAlign: "left",
        cursor: "pointer",
        marginBottom: "2px",
    },

    sidebarItemActive: {
        width: "100%",
        border: "none",
        background: "#374151",
        color: "#ffffff",
        padding: "10px",
        borderRadius: "6px",
        display: "flex",
        alignItems: "center",
        gap: "10px",
        fontSize: "13px",
        textAlign: "left",
        cursor: "pointer",
        marginBottom: "2px",
        fontWeight: 500,
    },

    sidebarBottom: {
        marginTop: "auto",
        borderTop:
            "1px solid rgba(255,255,255,0.08)",
        padding: "16px",
    },

    adminUser: {
        display: "flex",
        alignItems: "center",
        gap: "10px",
    },

    userAvatar: {
        width: "32px",
        height: "32px",
        borderRadius: "50%",
        background: "#374151",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: "13px",
        fontWeight: 600,
    },

    userName: {
        fontSize: "12px",
        color: "#e5e7eb",
    },

    userRole: {
        fontSize: "10px",
        color: "#9ca3af",
        marginTop: "2px",
    },


    // ==============================================
    // MAIN
    // ==============================================

    mainContent: {
        flex: 1,
        minWidth: 0,
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
    },

    topBar: {
        height: "72px",
        minHeight: "72px",
        background: "#ffffff",
        borderBottom: "1px solid #e5e7eb",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 30px",
        boxSizing: "border-box",
    },

    breadcrumb: {
        display: "flex",
        alignItems: "center",
        gap: "9px",
        fontSize: "13px",
        color: "#6b7280",
    },

    topBarRight: {
        display: "flex",
        alignItems: "center",
    },

    viewSiteButton: {
        border: "1px solid #d1d5db",
        background: "#ffffff",
        borderRadius: "6px",
        padding: "8px 12px",
        color: "#374151",
        fontSize: "12px",
        cursor: "pointer",
    },

    content: {
        padding: "30px",
        width: "100%",
        maxWidth: "1600px",
        boxSizing: "border-box",
        overflowX: "auto",
    },


    // ==============================================
    // PAGE HEADER
    // ==============================================

    contentHeader: {
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        marginBottom: "24px",
    },

    pageTitle: {
        margin: 0,
        fontSize: "24px",
        fontWeight: 600,
        color: "#111827",
    },

    pageSubtitle: {
        margin: "6px 0 0",
        color: "#6b7280",
        fontSize: "13px",
    },

    totalBadge: {
        background: "#ffffff",
        border: "1px solid #e5e7eb",
        borderRadius: "6px",
        padding: "8px 12px",
        fontSize: "12px",
        color: "#4b5563",
    },


    // ==============================================
    // TOOLBAR
    // ==============================================

    toolbar: {
        background: "#ffffff",
        border: "1px solid #e5e7eb",
        borderBottom: "none",
        padding: "12px 16px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
    },

    toolbarLeft: {
        display: "flex",
        alignItems: "center",
        gap: "7px",
    },

    toolbarLabel: {
        fontSize: "12px",
        color: "#6b7280",
    },

    pageSizeSelect: {
        border: "1px solid #d1d5db",
        borderRadius: "5px",
        padding: "6px 25px 6px 8px",
        fontSize: "12px",
        background: "#ffffff",
        color: "#374151",
    },

    refreshButton: {
        border: "1px solid #d1d5db",
        background: "#ffffff",
        borderRadius: "5px",
        padding: "7px 12px",
        fontSize: "12px",
        color: "#374151",
        cursor: "pointer",
    },


    // ==============================================
    // TABLE
    // ==============================================

    tableContainer: {
        background: "#ffffff",
        border: "1px solid #e5e7eb",
        overflowX: "auto",
    },

    table: {
        width: "100%",
        borderCollapse: "collapse",
        minWidth: "750px",
    },

    th: {
        textAlign: "left",
        padding: "12px 16px",
        fontSize: "11px",
        fontWeight: 600,
        color: "#6b7280",
        background: "#f9fafb",
        borderBottom: "1px solid #e5e7eb",
        whiteSpace: "nowrap",
    },

    td: {
        padding: "13px 16px",
        fontSize: "12px",
        color: "#4b5563",
        borderBottom: "1px solid #f0f1f3",
        whiteSpace: "nowrap",
        verticalAlign: "middle",
    },

    tableRow: {
        cursor: "pointer",
        background: "#ffffff",
    },

    nameCell: {
        color: "#111827",
        fontWeight: 500,
    },


    // ==============================================
    // STATUS
    // ==============================================

    statusNew: {
        display: "inline-block",
        padding: "4px 8px",
        borderRadius: "4px",
        background: "#ecfdf5",
        color: "#047857",
        fontSize: "11px",
        fontWeight: 500,
    },

    statusDefault: {
        display: "inline-block",
        padding: "4px 8px",
        borderRadius: "4px",
        background: "#f3f4f6",
        color: "#6b7280",
        fontSize: "11px",
    },

    roleUser: {
        display: "inline-block",
        padding: "4px 8px",
        borderRadius: "4px",
        background: "#eff6ff",
        color: "#2563eb",
        fontSize: "11px",
        fontWeight: 500,
    },

    roleAssistant: {
        display: "inline-block",
        padding: "4px 8px",
        borderRadius: "4px",
        background: "#ecfdf5",
        color: "#047857",
        fontSize: "11px",
        fontWeight: 500,
    },


    // ==============================================
    // LOADING / EMPTY / ERROR
    // ==============================================

    loading: {
        padding: "60px 20px",
        textAlign: "center",
        color: "#6b7280",
        fontSize: "13px",
    },

    emptyState: {
        padding: "60px 20px",
        textAlign: "center",
        color: "#9ca3af",
        fontSize: "13px",
    },

    errorBox: {
        background: "#fef2f2",
        border: "1px solid #fecaca",
        color: "#b91c1c",
        borderRadius: "6px",
        padding: "12px 14px",
        marginBottom: "15px",
        fontSize: "12px",
    },


    // ==============================================
    // PAGINATION
    // ==============================================

    pagination: {
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "15px 0",
    },

    paginationInfo: {
        color: "#6b7280",
        fontSize: "12px",
    },

    paginationControls: {
        display: "flex",
        alignItems: "center",
        gap: "4px",
        flexWrap: "wrap",
        justifyContent: "flex-end",
    },

    paginationButton: {
        border: "1px solid #d1d5db",
        background: "#ffffff",
        color: "#374151",
        borderRadius: "5px",
        padding: "7px 10px",
        fontSize: "11px",
        cursor: "pointer",
    },

    paginationActive: {
        border: "1px solid #374151",
        background: "#374151",
        color: "#ffffff",
        borderRadius: "5px",
        padding: "7px 10px",
        fontSize: "11px",
        cursor: "pointer",
    },

    paginationButtonDisabled: {
        border: "1px solid #e5e7eb",
        background: "#f9fafb",
        color: "#d1d5db",
        borderRadius: "5px",
        padding: "7px 10px",
        fontSize: "11px",
        cursor: "not-allowed",
    },


    // ==============================================
    // DASHBOARD
    // ==============================================

    dashboardGrid: {
        display: "grid",
        gridTemplateColumns:
            "repeat(3, minmax(0, 1fr))",
        gap: "18px",
        width: "100%",
    },

    statCard: {
        background: "#ffffff",
        border: "1px solid #e5e7eb",
        borderRadius: "8px",
        padding: "20px",
        minWidth: 0,
    },

    statLabel: {
        fontSize: "12px",
        color: "#6b7280",
    },

    statValue: {
        fontSize: "28px",
        fontWeight: 600,
        color: "#111827",
        marginTop: "8px",
    },


    // ==============================================
    // DETAIL OVERLAY
    // ==============================================

    detailOverlay: {
        position: "fixed",
        inset: 0,
        background: "rgba(0,0,0,0.35)",
        display: "flex",
        justifyContent: "flex-end",
        zIndex: 1000,
    },

    detailPanel: {
        width: "440px",
        maxWidth: "90vw",
        height: "100%",
        background: "#ffffff",
        boxShadow:
            "-10px 0 30px rgba(0,0,0,0.15)",
        display: "flex",
        flexDirection: "column",
    },

    detailHeader: {
        padding: "20px",
        borderBottom: "1px solid #e5e7eb",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
    },

    detailTitle: {
        margin: 0,
        fontSize: "18px",
        fontWeight: 600,
        color: "#111827",
    },

    detailSubtitle: {
        margin: "4px 0 0",
        fontSize: "12px",
        color: "#6b7280",
        wordBreak: "break-all",
    },

    closeButton: {
        width: "32px",
        height: "32px",
        border: "none",
        background: "#f3f4f6",
        borderRadius: "5px",
        fontSize: "20px",
        color: "#4b5563",
        cursor: "pointer",
        flexShrink: 0,
    },

    detailBody: {
        padding: "20px",
        overflowY: "auto",
    },

    detailRow: {
        padding: "14px 0",
        borderBottom: "1px solid #f0f1f3",
    },

    detailLabel: {
        fontSize: "10px",
        fontWeight: 600,
        color: "#9ca3af",
        textTransform: "uppercase",
        letterSpacing: "0.05em",
        marginBottom: "5px",
    },

    detailValue: {
        fontSize: "13px",
        color: "#374151",
        wordBreak: "break-word",
        whiteSpace: "pre-wrap",
    },
};


export default AdminPanel;