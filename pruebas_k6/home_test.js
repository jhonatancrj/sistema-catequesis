import http from 'k6/http';
import { check } from 'k6';

export let options = {
    vus: 10,
    duration: '30s',
};

export default function () {

    let res = http.get('http://127.0.0.1:8000/');

    check(res, {
        'status 200': (r) => r.status === 200,
    });

}