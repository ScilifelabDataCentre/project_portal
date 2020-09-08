import axios from 'axios';

import {getCsrfHeader} from '../helpers.js';

export function getCollection ({ commit, dispatch }, id) {
  return new Promise((resolve, reject) => {
    axios
      .get('/api/collection/' + id + '/')
      .then((response) => {
        commit('updateCollection', response.data.collection);
        resolve(response);
      })
      .catch((err) => {
        commit('updateCollection', {});
        reject(err);
      });
  });
}

export function getCollections ({ commit, dispatch }) {
  return new Promise((resolve, reject) => {
    axios
      .get('/api/collection/')
      .then((response) => {
        commit('updateCollections', response.data.collections);
        resolve(response);
      })
      .catch((err) => {
        commit('updateCollections', []);
        reject(err);
      });
  });
}

export function deleteCollection (context, payload) {
  return new Promise((resolve, reject) => {
    axios
      .delete('/api/collection/' + payload + '/',
              {
                headers: getCsrfHeader(),
              })
      .then((response) => {
        resolve(response);
      })
      .catch(function (err) {
        reject(err);
      });
  });
}

export function saveCollection (context, payload) {
  return new Promise((resolve, reject) => {
    let collectionUuid = payload.id;
    delete payload.id
    if (collectionUuid === '-1') {
      axios
        .post('/api/collection/',
              payload,
              {
                headers: getCsrfHeader(),
              })
        .then((response) => {
          resolve(response);
        })
        .catch(function (err) {
          reject(err);
        });
    }
    else {
      axios
        .patch('/api/collection/' + collectionUuid + '/',
               payload,
               {
                 headers: getCsrfHeader(),
               })
        .then((response) => {
          resolve(response);
        })
        .catch(function (err) {
          reject(err);
        });
    }
  });
}
