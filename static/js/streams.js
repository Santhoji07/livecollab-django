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
    client.on('user-published', handleUserJoined)

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

let handleUserJoined = async (user, mediaType) => {
    remoteUsers[user.uid] = user
    await client.subscribe(user, mediaType)

    if (mediaType === 'video') {
        let player = document.getElementById(`user-container-${user.uid}`)
        if (player != null) {
            player.remove()
        }

        player = `<div class="video-container" id="user-container-${user.uid}">
                    <div class="username-wrapper"><span class="user-name">My name</span></div>
                    <div class="video-player" id="user-${user.uid}"></div>
                </div>`

        document.getElementById('video-streams').insertAdjacentHTML('beforeend', player)
    
        user.videoTrack.play(`user-${user.uid}`)
    }

    if(mediaType==='audio') {
        user.audioTrack.play()
    }
}

// Call the function to join the channel and display the local stream.
joinAndDisplayLocalStream()
