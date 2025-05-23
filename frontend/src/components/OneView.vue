<template>
    <dive class="hello">
        <dive class="title-color">d [[ text ]] b</dive>
    </dive>
</template>

<script>
import axios from 'axios';

export default {
    name: 'OneView',
    props: {
        msg: String
    },
    data() {
        return {
            text: null
        }
    },
    mounted() {
        axios
            .get('http://localhost:8000/api/sample')
            .then(response => {
                this.text = response.data;
            })
            .then(response => {
                console.log('status:', response.status);
                console.log('axiosGetData:', response.data);
            })
            .catch(err => {
                console.error('Error fetching data:', err);
            });
    }
}
</script>

<style scoped>
.title-color {
    color: #42b983;
}
</style>