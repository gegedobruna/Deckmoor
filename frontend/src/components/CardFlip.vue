<template>
    <div class="card-flip-container" @click="flipCard">
        <div class="card-flip" :class="{ flipped: isFlipped }">
            <!-- Front Face -->
            <div class="card-face front">
                <img 
                    :src="frontImage || '/placeholder.jpg'" 
                    :alt="card.name" 
                />
            </div>
            <!-- Back Face -->
            <div class="card-face back">
                <img 
                    :src="backImage || '/placeholder.jpg'" 
                    :alt="card.name" 
                />
            </div>
        </div>
    </div>
</template>

<script>
export default {
    props: {
        card: Object,
    },
    data() {
        return {
            isFlipped: false,
        };
    },
    computed: {
        frontImage() {
            return this.card?.card_faces?.[0]?.image_uris?.normal || this.card?.image_uris?.normal;
        },
        backImage() {
            return this.card?.card_faces?.[1]?.image_uris?.normal || null;
        }
    },
    methods: {
        flipCard() {
            if (this.backImage) {
                this.isFlipped = !this.isFlipped;
            }
        }
    }
};
</script>

<style scoped>
.card-flip-container {
    perspective: 1000px;
    width: 150px;
    height: 210px;
}
.card-flip {
    position: relative;
    width: 100%;
    height: 100%;
    transition: transform 0.6s;
    transform-style: preserve-3d;
}
.card-flip.flipped {
    transform: rotateY(180deg);
}
.card-face {
    position: absolute;
    width: 100%;
    height: 100%;
    backface-visibility: hidden;
    border-radius: 5px;
    overflow: hidden;
}
.card-face img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 5px;
}
.back {
    transform: rotateY(180deg);
}
</style>
