const APP_ID = '351d9881f5d3413ba18e08949844fddb'
// Get the channel name and token from the session storage.
const CHANNEL = sessionStorage.getItem('room')
const TOKEN = sessionStorage.getItem('token')

// Get the UID (User ID) from the session storage and convert it to a number.
let UID = Number(sessionStorage.getItem('UID'))

// Get the user's name from session storage.
let NAME = sessionStorage.getItem('name')

// Create an Agora client instance for RTC (Real-Time Communication) using VP8 codec for video.
const client = AgoraRTC.createClient({ mode: 'rtc', codec: 'vp8' })

// Declare variables for storing local media tracks (microphone and camera) and remote users.
let localTracks = []
let remoteUsers = {}

// Async function to join the Agora channel and display the local video stream.
let joinAndDisplayLocalStream = async () => {
    // Display the current room name in the UI.
    document.getElementById('room-name').innerText = CHANNEL

    // Set up event listeners for when a remote user publishes (joins the call) or leaves.
    client.on('user-published', handleUserJoined)  // When a remote user publishes their media.
    client.on('user-left', handleUserLeft)         // When a remote user leaves the call.

    try {
        // Join the Agora channel using the app ID, channel name, token, and UID.
        await client.join(APP_ID, CHANNEL, TOKEN, UID)
    }
    catch (error) {
        // If there's an error joining the channel, log it and redirect to the home page.
        console.error(error)
        window.open('/', '_self')
    }

    // Get local microphone and camera tracks.
    localTracks = await AgoraRTC.createMicrophoneAndCameraTracks()

    // Create a new member for the session by calling the server.
    let member = await createMember()

    // Create an HTML element to display the local user's video stream and their name.
    let player = `<div class="video-container" id="user-container-${UID}">
                    <div class="username-wrapper"><span class="user-name">${member.name}</span></div>
                    <div class="video-player" id="user-${UID}"></div>
                </div>`

    // Add the video player HTML to the DOM under the 'video-streams' element.
    document.getElementById('video-streams').insertAdjacentHTML('beforeend', player)

    // Play the local video track inside the video player.
    localTracks[1].play(`user-${UID}`)

    // Publish both the local microphone and camera tracks to the Agora channel, so other users can see and hear the local user.
    await client.publish([localTracks[0], localTracks[1]])
}

// Function to handle when a remote user joins and publishes media (video/audio).
let handleUserJoined = async (user, mediaType) => {
    // Add the remote user to the 'remoteUsers' object for tracking.
    remoteUsers[user.uid] = user

    // Subscribe to the remote user's media (either video or audio).
    await client.subscribe(user, mediaType)

    // If the remote user's media is a video stream.
    if (mediaType === 'video') {
        // Remove any existing video container for the user to avoid duplicates.
        let player = document.getElementById(`user-container-${user.uid}`)
        if (player != null) {
            player.remove()
        }

        // Get the remote user's member information from the server.
        let member = await getMember(user)

        // Create a new HTML structure for the remote user's video stream.
        player = `<div class="video-container" id="user-container-${user.uid}">
                    <div class="username-wrapper"><span class="user-name">${member.name}</span></div>
                    <div class="video-player" id="user-${user.uid}"></div>
                </div>`

        // Add the remote user's video stream to the DOM under the 'video-streams' element.
        document.getElementById('video-streams').insertAdjacentHTML('beforeend', player)

        // Play the remote user's video track in the respective video player.
        user.videoTrack.play(`user-${user.uid}`)
    }

    // If the remote user's media is an audio stream.
    if (mediaType === 'audio') {
        // Play the remote user's audio track (there's no specific UI for audio).
        user.audioTrack.play()
    }
}

// Function to handle when a remote user leaves the call.
let handleUserLeft = async (user) => {
    // Remove the user from the 'remoteUsers' object.
    delete remoteUsers[user.uid]
    // Remove the remote user's video container from the DOM.
    document.getElementById(`user-container-${user.uid}`).remove()
}

// Function to leave the channel and stop the local media streams.
let leaveAndRemoveLocalStream = async () => {
    // Stop and close each local media track (microphone and camera).
    for (let i = 0; localTracks.length > i; i++) {
        localTracks[i].stop()
        localTracks[i].close()
    }

    // Leave the Agora channel.
    await client.leave()

    // Delete the local user's member information from the server.
    deleteMember()

    // Redirect to the home page after leaving.
    window.open('/', '_self')
}

// Function to toggle the local camera (turn on/off).
let toggleCamera = async (e) => {
    // If the camera is muted (off), unmute it and change the button color to white.
    if (localTracks[1].muted) {
        await localTracks[1].setMuted(false)
        e.target.style.backgroundColor = '#fff'
    } else {
        // If the camera is unmuted (on), mute it and change the button color to red.
        await localTracks[1].setMuted(true)
        e.target.style.backgroundColor = 'rgb(255, 80, 80, 1)'
    }
}

// Function to toggle the local microphone (turn on/off).
let toggleMic = async (e) => {
    // If the microphone is muted (off), unmute it and change the button color to white.
    if (localTracks[0].muted) {
        await localTracks[0].setMuted(false)
        e.target.style.backgroundColor = '#fff'
    } else {
        // If the microphone is unmuted (on), mute it and change the button color to red.
        await localTracks[0].setMuted(true)
        e.target.style.backgroundColor = 'rgb(255, 80, 80, 1)'
    }
}

// Function to create a new member by sending a POST request to the server.
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

// Function to get a member's information based on their UID and room name.
let getMember = async (user) => {
    let response = await fetch(`/get_member/?UID=${user.uid}&room_name=${CHANNEL}`)
    let member = await response.json()

    return member
}

// Function to delete a member by sending a POST request to the server.
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

// When the window is about to unload, call the deleteMember function to remove the user.
window.addEventListener('beforeunload', deleteMember)

// Add event listeners for the leave, camera, and microphone buttons.
document.getElementById('leave-btn').addEventListener('click', leaveAndRemoveLocalStream)
document.getElementById('camera-btn').addEventListener('click', toggleCamera)
document.getElementById('mic-btn').addEventListener('click', toggleMic)
