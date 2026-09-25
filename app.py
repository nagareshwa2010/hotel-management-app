// அறை விவரங்களின் பட்டியல் (Rooms Data)
const roomTypes = [
  {
    id: 1,
    name: "Standard Room",
    price: 2000, // ஒரு நாளுக்கான கட்டணம் (ரூபாயில்)
    capacity: "2 Guests",
    features: ["Free Wi-Fi", "Air Conditioning", "TV"],
    description: "குறைந்த செலவில் வசதியாகத் தங்க விரும்பும் தனிநபர்கள் மற்றும் தம்பதிகளுக்கு ஏற்றது."
  },
  {
    id: 2,
    name: "Deluxe Suite",
    price: 4000,
    capacity: "2 Guests",
    features: ["Free Wi-Fi", "King Size Bed", "City View", "Breakfast Included"],
    description: "அழகான நகர்ப்புறக் காட்சியுடன் கூடிய சிறந்த ஆடம்பர அனுபவம்."
  },
  {
    id: 3,
    name: "Executive Suite",
    price: 7000,
    capacity: "3 Guests",
    features: ["Free Wi-Fi", "Work Desk", "Ocean View", "Mini Bar"],
    description: "பிசினஸ் பயணிகளுக்கான பிரத்யேக வேலை செய்யும் வசதிகள் கொண்ட அறை."
  },
  {
    id: 4,
    name: "Family Suite",
    price: 9000,
    capacity: "4 to 6 Guests",
    features: ["2 King Beds", "Living Room", "Kids Play Area Access", "Free Breakfast"],
    description: "முழு குடும்பத்துடன் இணைந்து மகிழ்ச்சியாகத் தங்க விசாலமான இடம்."
  },
  {
    id: 5,
    name: "Presidential Suite",
    price: 15000,
    capacity: "4 Guests",
    features: ["Private Jacuzzi", "Personal Butler", "Panoramic View", "VIP Access"],
    description: "உயர்தர ராயல் அனுபவம் மற்றும் தனிநபர் கவனிப்புடன் கூடிய பிரம்மாண்ட அறை."
  },
  {
    id: 6,
    name: "Penthouse Suite",
    price: 20000,
    capacity: "4 Guests",
    features: ["Top Floor View", "Private Terrace", "Plunge Pool", "Luxury Dining Area"],
    description: "ஹோட்டலின் மேல் தளத்தில் அமைந்துள்ள தனித்துவமான மற்றும் மிக உயர்தர வசதிகள் கொண்ட அறை."
  }
];

// அறைகளை திரையில் காண்பிக்கும் செயல்பாடு (Function to render rooms)
function displayRooms(rooms) {
  rooms.forEach(room => {
    console.log(`Room: ${room.name} | Price: ₹${room.price} | Capacity: ${room.capacity}`);
  });
}

// செயல்பாட்டை இயக்குதல்
displayRooms(roomTypes);
