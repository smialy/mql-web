(function(){


    async function send(query, params){
        console.clear();
        const resp = await fetch('/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id: 1,
                query,
                params
            })
        });
        try{
            const response = await resp.json();
            if(response.errors){
                for(let error of response.errors){
                    console.log(error);
                }
            }else{
                console.log(response.data);
            }
        }catch(e){}
    }

    class UI {
        constructor(){
            this.$form = document.querySelector('form');
            this.$query = document.querySelector('textarea.query');
            this.$params = document.querySelector('textarea.params');
            this.$queries = document.querySelector('#queries');
            this.addEvents()
        }
        addEvents(){
            this.$form.addEventListener('submit', e => {
                e.preventDefault();
                const query = this.$query.value;
                const params = this.validParams(this.$params.value);
                send(query, params);
            });
        }
        validParams(text){
            if(text){
                try{
                    return JSON.parse(text);
                }catch(e){
                    console.log(e);
                }
            }
            return null;
        }
    }

    class Queries{
        constructor(){
            this.queries = Queries.load();
        }
        add(query, params){

        }
        static load(){
            try{
                const data = JSON.parse(localStorage.getItem('queries'));
                return data || [];
            }catch(e){
            }
            return [];
        }
        static save(queries){
            const data = JSON.stringify(queries);
            localStorage.setItem('queries', data);
        }
    }

    const ui = new UI();

})();