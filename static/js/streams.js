// Define the App ID for Agora, the unique identifier for your Agora project.
const APP_ID = '351d9881f5d3413ba18e08949844fddb'
// Get the channel name and token from the session storage (where they're saved when the user joins).
const CHANNEL = sessionStorage.getItem('room')
const TOKEN = sessionStorage.getItem('token')

// Retrieve the user's unique identifier (UID) and name from the session storage.
let UID = Number(sessionStorage.getItem('UID'))
let NAME = sessionStorage.getItem('name')

// Create an Agora client instance for Real-Time Communication (RTC), using VP8 codec for video.
const client = AgoraRTC.createClient({ mode: 'rtc', codec: 'vp8' })

// Declare variables to store local media tracks (microphone and camera) and remote users.
let localTracks = []
let remoteUsers = {}

// Function to join the channel, create and display the local stream, and subscribe to remote users.
let joinAndDisplayLocalStream = async () => {
    document.getElementById('room-name').innerText = CHANNEL;

    // Set up event listeners for new users joining and leaving the channel.
    client.on('user-published', handleUserJoined);
    client.on('user-left', handleUserLeft);

    try {
        // Attempt to join the Agora channel using the provided App ID, channel, token, and UID.
        await client.join(APP_ID, CHANNEL, TOKEN, UID);
    } catch (error) {
        console.error("Error joining channel:", error);
        window.open('/', '_self'); // Redirect to home if joining fails.
    }

    // Create the local media tracks (audio and video).
    localTracks = await AgoraRTC.createMicrophoneAndCameraTracks();
    let member = await createMember(); // Create a new member for the server.

    // Generate the HTML to display the local video feed.
    let player = `<div class="video-container" id="user-container-${UID}">
                    <div class="username-wrapper"><span class="user-name">${member.name}</span></div>
                    <div class="video-player" id="user-${UID}"></div>
                </div>`;
    document.getElementById('video-streams').insertAdjacentHTML('beforeend', player);

    // Play the local video stream and publish it to the channel.
    localTracks[1].play(`user-${UID}`);
    await client.publish([localTracks[0], localTracks[1]]);

    // Subscribe to existing remote users if any are already in the channel.
    for (let user of client.remoteUsers) {
        console.log("Subscribing to existing user:", user.uid);
        await subscribeToRemoteUser(user);
    }
};

// Function to subscribe to a remote user's media (audio and video).
let subscribeToRemoteUser = async (user) => {
    try {
        // Subscribe to the user's video and audio streams.
        await client.subscribe(user, 'video').catch(console.error);
        await client.subscribe(user, 'audio').catch(console.error);

        // If the user is new, create the UI for their video feed.
        let player = document.getElementById(`user-container-${user.uid}`);
        if (!player) {
            let member = await getMember(user); // Fetch remote user information from the server.
            player = `<div class="video-container" id="user-container-${user.uid}">
                        <div class="username-wrapper"><span class="user-name">${member.name}</span></div>
                        <div class="video-player" id="user-${user.uid}"></div>
                    </div>`;
            document.getElementById('video-streams').insertAdjacentHTML('beforeend', player);
        }

        // Play the remote user's video and audio streams if available.
        if (user.videoTrack) {
            user.videoTrack.play(`user-${user.uid}`);
        }

        if (user.audioTrack) {
            user.audioTrack.play();
        }
    } catch (error) {
        console.error("Error subscribing to user:", user.uid, error);
    }
};

// Event handler for when a new user joins the channel.
let handleUserJoined = async (user, mediaType) => {
    remoteUsers[user.uid] = user;
    await subscribeToRemoteUser(user);
};

// Event handler for when a user leaves the channel.
let handleUserLeft = async (user) => {
    delete remoteUsers[user.uid];
    document.getElementById(`user-container-${user.uid}`)?.remove();
};

// Function to leave the channel, stop local media tracks, and redirect to the home page.
let leaveAndRemoveLocalStream = async () => {
    // Stop and close all local media tracks (camera and microphone).
    for (let i = 0; localTracks.length > i; i++) {
        localTracks[i].stop()
        localTracks[i].close()
    }

    // Leave the Agora channel.
    await client.leave()

    // Delete the local user's member information from the server.
    deleteMember()

    // Redirect to the home page after leaving the channel.
    window.open('/', '_self')
}

// Function to toggle the local camera on/off.
let toggleCamera = async (e) => {
    // If the camera is off (muted), unmute it and change the button style.
    if (localTracks[1].muted) {
        await localTracks[1].setMuted(false)
        e.target.style.backgroundColor = '#fff'
    } else {
        // If the camera is on, mute it and change the button style.
        await localTracks[1].setMuted(true)
        e.target.style.backgroundColor = 'rgb(255, 80, 80, 1)'
    }

    // Re-subscribe to remote users after toggling the camera.
    for (let user of client.remoteUsers) {
        console.log("Re-subscribing to user:", user.uid);
        await subscribeToRemoteUser(user);
    }
}

// Function to toggle the local microphone on/off.
let toggleMic = async (e) => {
    // If the microphone is off (muted), unmute it and change the button style.
    if (localTracks[0].muted) {
        await localTracks[0].setMuted(false)
        e.target.style.backgroundColor = '#fff'
    } else {
        // If the microphone is on, mute it and change the button style.
        await localTracks[0].setMuted(true)
        e.target.style.backgroundColor = 'rgb(255, 80, 80, 1)'
    }

    // Re-subscribe to remote users after toggling the microphone.
    for (let user of client.remoteUsers) {
        console.log("Re-subscribing to user:", user.uid);
        await subscribeToRemoteUser(user);
    }
}

// Function to create a new member on the server.
let createMember = async () => {
    let response = await fetch('/create_member/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 'name': NAME, 'room_name': CHANNEL, 'UID': UID })
    })

    let member = await response.json()
    return member
}

// Function to retrieve member details from the server based on UID.
let getMember = async (user) => {
    let response = await fetch(`/get_member/?UID=${user.uid}&room_name=${CHANNEL}`)
    let member = await response.json()

    return member
}

// Function to delete the member from the server when they leave the channel.
let deleteMember = async () => {
    let response = await fetch('/delete_member/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 'name': NAME, 'room_name': CHANNEL, 'UID': UID })
    })

    let member = await response.json()
}

// Call the function to join the channel and display the local stream.
joinAndDisplayLocalStream()

// Add event listener to delete the member when the window is about to unload (user leaves the page).
window.addEventListener('beforeunload', deleteMember)

// Add event listeners for the leave, camera, and microphone buttons.
document.getElementById('leave-btn').addEventListener('click', leaveAndRemoveLocalStream)
document.getElementById('camera-btn').addEventListener('click', toggleCamera)
document.getElementById('mic-btn').addEventListener('click', toggleMic)
