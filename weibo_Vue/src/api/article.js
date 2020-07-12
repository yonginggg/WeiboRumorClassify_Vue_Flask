import http from '@/utils/http';

export const apiArticleSave = (data, config) => {
    return http.post('article/save', data, config);
};
export const apiArticleList = (data, config) => {
    return http.post('article/list', data, config);
};
export const apiAllArticle = (data, config) => {
    return http.post('article/allarticle', data, config);
};
export const apiUserCommentList = (data, config) => {
    return http.post('article/comment', data, config);
};
export const apiArticleGet = (data, config) => {
    return http.post('article/fetch', data, config);
};

export const apiArticleCount = (data, config) => {
    return http.post('article/count', data, config);
};


