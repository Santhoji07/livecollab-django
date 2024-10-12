const APP_ID = '351d9881f5d3413ba18e08949844fddb'
const CHANNEL = 'main'
const TOKEN = '007eJxTYJhS8+bBJvOyp7oyu9ZJmSyP4jl/d+a5qNv7OZZWmV+Z1l+hwGBsaphiaWFhmGaaYmxiaJyUaGiRamBhaWJpYWKSlpKSdD6SM70hkJHhxO/jzIwMEAjiszDkJmbmMTAAALpaISk='
let UID;

// Create a client instance using AgoraRTC with 'rtc' mode (Real-Time Communication) and VP8 codec for video.
const client = AgoraRTC.createClient({ mode: 'rtc', codec: 'vp8' })

// Declare variables for local media tracks and remote users.
let localTracks = []
let remoteUsers = {}

// Async function to join the channel and display the local video stream.
let joinAndDisplayLocalStream = async () => {
    // Listen for when a remote user publishes their media (video/audio).
    client.on('user-published', handleUserJoined)
    client.on('user-left', handleUserLeft)

    // Join the Agora channel using the app ID, channel name, and token. UID (User ID) is generated.
    UID = await client.join(APP_ID, CHANNEL, TOKEN, null)

    // Create and get the local microphone and camera tracks.
    localTracks = await AgoraRTC.createMicrophoneAndCameraTracks()

    // Create an HTML structure to display the user's video stream and name.
    let player = `<div class="video-container" id="user-container-${UID}">
                    <div class="username-wrapper"><span class="user-name">My name</span></div>
                    <div class="video-player" id="user-${UID}"></div>
                </div>`

    // Add the newly created player HTML to the 'video-streams' element in the DOM.
    document.getElementById('video-streams').insertAdjacentHTML('beforeend', player)

    // Play the local video track inside the 'video-player' element by using its UID.
    localTracks[1].play(`user-${UID}`)

    // Publish both local microphone and camera tracks to the Agora channel, making them available to other users.
    await client.publish([localTracks[0], localTracks[1]])
}

// Function to handle when a remote user joins and publishes media (video/audio).
let handleUserJoined = async (user, mediaType) => {
    // Add the remote user to the 'remoteUsers' object.
    remoteUsers[user.uid] = user
    // Subscribe to the remote user's media (either video or audio).
    await client.subscribe(user, mediaType)

    // If the media type is video, display the remote user's video stream.
    if (mediaType === 'video') {
        // Remove the video container if it already exists to avoid duplicates.
        let player = document.getElementById(`user-container-${user.uid}`)
        if (player != null) {
            player.remove()
        }

        // Create and add a new HTML structure for the remote user's video stream.
        player = `<div class="video-container" id="user-container-${user.uid}">
                    <div class="username-wrapper"><span class="user-name">My name</span></div>
                    <div class="video-player" id="user-${user.uid}"></div>
                </div>`

        document.getElementById('video-streams').insertAdjacentHTML('beforeend', player)

        // Play the remote user's video track in the newly created 'video-player' element.
        user.videoTrack.play(`user-${user.uid}`)
    }

    // If the media type is audio, play the remote user's audio track.
    if (mediaType === 'audio') {
        user.audioTrack.play()
    }
}

let handleUserLeft = async (user) => {
    delete remoteUsers[user.uid]
    document.getElementById(`user-container-${user.uid}`).remove()

let leaveAndRemoveLocalStream = async () => {
    for (let i=0; localTracks.length > i; i++){
        localTracks[i].stop()
        localTracks[i].close()
    }

    await client.leave()
    window.open('/', '_self')
}

let toggleCamera = async (e) => {
    if(localTracks[1].muted){
        await localTracks[1].setMuted(false)
        e.target.style.backgroundColor = '#fff'
    }else{
        await localTracks[1].setMuted(true)
        e.target.style.backgroundColor = 'rgb(255, 80, 80, 1)'
    }
}

let toggleMic = async (e) => {
    if(localTracks[0].muted){
        await localTracks[0].setMuted(false)
        e.target.style.backgroundColor = '#fff'
    }else{
        await localTracks[0].setMuted(true)
        e.target.style.backgroundColor = 'rgb(255, 80, 80, 1)'
    }
}
// Call the function to join the channel and display the local stream.
joinAndDisplayLocalStream()

document.getElementById('leave-btn').addEventListener('click', leaveAndRemoveLocalStream)
document.getElementById('camera-btn').addEventListener('click', toggleCamera)
document.getElementById('mic-btn').addEventListener('click', toggleMic)