#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>
#include <mongoose.h>
#include <cjson/cJSON.h>

#define MAX_HORSES 8
#define TRACK_LENGTH 500
#define MAX_PLAYERS 10
#define NPC_HORSE_COUNT 6
#define HORSE_NAME_LEN 16

struct horse {
    char name[HORSE_NAME_LEN];
    unsigned char horse_emblem_id;
    unsigned char last_roll;
    unsigned int position;
    int is_player;
} __attribute__((packed));

struct race_state {
    struct horse horses[MAX_HORSES];
    int horse_count;
    int race_active;
    int winner_index;
    time_t race_start;
    time_t last_npc_move;
};

struct player_session {
    char session_id[32];
    int player_horse_index;
    struct race_state race;
    int game_active;
    time_t created_at;
    double last_player_move;
};

static struct player_session sessions[MAX_PLAYERS];
static int session_count = 0;

static const char* npc_names[] = {
    "Thunder", "Lightning", "Storm", "Blaze", "Fury", "Spirit"
};

static double get_time_ms() {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec + tv.tv_usec / 1000000.0;
}

static void sanitize_name_for_display(const char* input, char* output, size_t output_size) {
    size_t j = 0;
    for (size_t i = 0; i < HORSE_NAME_LEN && j < output_size - 1; i++) {
        if (input[i] >= 32 && input[i] <= 126) {
            output[j++] = input[i];
        }
    }
    output[j] = '\0';
}

static void init_race(struct race_state* race) {
    memset(race, 0, sizeof(struct race_state));
    race->race_active = 1;
    race->winner_index = -1;
    race->race_start = time(NULL);
    race->last_npc_move = time(NULL);

    for (int i = 0; i < NPC_HORSE_COUNT; i++) {
        struct horse* npc = &race->horses[i];
        strncpy(npc->name, npc_names[i], sizeof(npc->name) - 1);
        npc->name[sizeof(npc->name) - 1] = '\0';
        npc->horse_emblem_id = i % 4;
        npc->last_roll = 5;
        npc->position = 0;
        npc->is_player = 0;
    }
    race->horse_count = NPC_HORSE_COUNT;
}

static void update_npcs(struct race_state* race) {
    if (!race || !race->race_active) return;
    time_t now = time(NULL);
    if (now - race->last_npc_move < 1) return;

    race->last_npc_move = now;

    for (int i = 0; i < race->horse_count; i++) {
        if (race->horses[i].is_player || race->horses[i].position >= TRACK_LENGTH) continue;
        int movement = (rand() % 50) + 10;
        race->horses[i].position += movement;
        if (race->horses[i].position >= TRACK_LENGTH && race->winner_index == -1) {
            race->winner_index = i;
            race->race_active = 0;
        }
    }
}

static struct player_session* get_or_create_session() {
    struct player_session* session = &sessions[0];
    if (session_count == 0) {
        session_count = 1;
    }
    init_race(&session->race);
    strncpy(session->session_id, "default_session", sizeof(session->session_id) - 1);
    session->created_at = time(NULL);
    session->game_active = 0;
    session->player_horse_index = -1;
    session->last_player_move = 0;
    return session;
}

static void set_horse_name_and_emblem(struct horse* h, const char* name_str, unsigned char emblem_id) {
    h->horse_emblem_id = emblem_id;
    strcpy(h->name, name_str);
}

static void handle_setup(struct mg_connection *c, struct mg_http_message *hm) {
    cJSON *json = cJSON_Parse(hm->body.ptr);
    if (!json) {
        mg_http_reply(c, 400, "Content-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\n", "{\"success\":false,\"message\":\"Invalid JSON\"}");
        return;
    }

    cJSON *horse_name_item = cJSON_GetObjectItem(json, "horseName");
    cJSON *emblem_id_item = cJSON_GetObjectItem(json, "emblemId");

    if (!horse_name_item || !cJSON_IsString(horse_name_item)) {
        cJSON_Delete(json);
        mg_http_reply(c, 400, "Content-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\n", "{\"success\":false,\"message\":\"Missing or invalid horseName\"}");
        return;
    }
    
    unsigned char emblem_id = 0;
    if (emblem_id_item && cJSON_IsNumber(emblem_id_item)) {
        emblem_id = emblem_id_item->valueint % 4;
    }

    struct player_session* session = get_or_create_session();
    session->player_horse_index = session->race.horse_count;
    struct horse* player_horse = &session->race.horses[session->player_horse_index];

    player_horse->last_roll = 50;
    player_horse->position = 0;
    player_horse->is_player = 1;
    session->last_player_move = get_time_ms();

    set_horse_name_and_emblem(player_horse, horse_name_item->valuestring, emblem_id);

    session->race.horse_count++;
    session->game_active = 1;
    cJSON_Delete(json);

    cJSON *response_json = cJSON_CreateObject();
    cJSON_AddBoolToObject(response_json, "success", 1);
    cJSON_AddNumberToObject(response_json, "last_roll", player_horse->last_roll);
    cJSON_AddNumberToObject(response_json, "player_index", session->player_horse_index);
    cJSON *horses_array = cJSON_CreateArray();
    
    for (int i = 0; i < session->race.horse_count; i++) {
        cJSON *horse_obj = cJSON_CreateObject();
        char clean_name[32];
        sanitize_name_for_display(session->race.horses[i].name, clean_name, sizeof(clean_name));
        cJSON_AddStringToObject(horse_obj, "name", clean_name);
        cJSON_AddNumberToObject(horse_obj, "position", session->race.horses[i].position);
        cJSON_AddBoolToObject(horse_obj, "is_player", session->race.horses[i].is_player);
        cJSON_AddItemToArray(horses_array, horse_obj);
    }
    cJSON_AddItemToObject(response_json, "horses", horses_array);
    
    char *response_str = cJSON_PrintUnformatted(response_json);
    mg_http_reply(c, 200, 
        "Content-Type: application/json\r\n"
        "Access-Control-Allow-Origin: *\r\n"
        "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
        "Access-Control-Allow-Headers: Content-Type\r\n", "%s", response_str);
    
    free(response_str);
    cJSON_Delete(response_json);
}

static void handle_dash(struct mg_connection *c, struct mg_http_message *hm) {
    struct player_session* session = &sessions[0];
    if (!session->game_active || session->player_horse_index == -1) {
        mg_http_reply(c, 400, "Content-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\n", "{\"success\":false,\"message\":\"Game not started.\"}");
        return;
    }

    time_t now = time(NULL);
    double precise_now = get_time_ms();

    if (precise_now - session->last_player_move < 1.0) {
        mg_http_reply(c, 400, "Content-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\n", "{\"success\":false,\"message\":\"Please wait before your next dash.\"}");
        return;
    }

    update_npcs(&session->race);

    struct horse* player_horse = &session->race.horses[session->player_horse_index];
    int winner = 0;
    double bonus = 0;

    if(session->race.race_active) {
        int movement = player_horse->last_roll;
        double time_since = precise_now - session->last_player_move;
        double deviation = fabs(time_since - 1.5);
        bonus = 10*fmax(0, 1.0 - sqrt(deviation));
        session->last_player_move = precise_now;
        player_horse->last_roll = (rand() % 50) + (int)bonus;

        player_horse->position += movement;

        if (player_horse->position >= TRACK_LENGTH) {
            player_horse->position = TRACK_LENGTH;
            if (session->race.winner_index == -1) {
                session->race.winner_index = session->player_horse_index;
                session->race.race_active = 0;
                winner = 1;
            }
        }
    } else if (session->race.winner_index == session->player_horse_index) {
        winner = 1;
    }

    cJSON *response_json = cJSON_CreateObject();
    cJSON_AddBoolToObject(response_json, "success", 1);
    cJSON_AddNumberToObject(response_json, "last_roll", player_horse->last_roll);
    cJSON_AddNumberToObject(response_json, "timing_bonus", (int)bonus);
    cJSON_AddBoolToObject(response_json, "winner", winner);
    cJSON_AddBoolToObject(response_json, "race_over", !session->race.race_active);

    cJSON *horses_array = cJSON_CreateArray();
    for (int i = 0; i < session->race.horse_count; i++) {
        cJSON *horse_obj = cJSON_CreateObject();
        char clean_name[32];
        sanitize_name_for_display(session->race.horses[i].name, clean_name, sizeof(clean_name));
        cJSON_AddStringToObject(horse_obj, "name", clean_name);
        int pos = session->race.horses[i].position > TRACK_LENGTH ? TRACK_LENGTH : session->race.horses[i].position;
        cJSON_AddNumberToObject(horse_obj, "position", pos);
        cJSON_AddBoolToObject(horse_obj, "is_player", session->race.horses[i].is_player);
        cJSON_AddItemToArray(horses_array, horse_obj);
    }
    cJSON_AddItemToObject(response_json, "horses", horses_array);

    char *response_str = cJSON_PrintUnformatted(response_json);
    mg_http_reply(c, 200, 
        "Content-Type: application/json\r\n"
        "Access-Control-Allow-Origin: *\r\n"
        "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
        "Access-Control-Allow-Headers: Content-Type\r\n", "%s", response_str);

    free(response_str);
    cJSON_Delete(response_json);
}

static void fn(struct mg_connection *c, int ev, void *ev_data, void *fn_data) {
    if (ev == MG_EV_HTTP_MSG) {
        struct mg_http_message *hm = (struct mg_http_message *) ev_data;
        
        if (strncmp(hm->method.ptr, "OPTIONS", hm->method.len) == 0) {
            mg_http_reply(c, 200, 
                "Access-Control-Allow-Origin: *\r\n"
                "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
                "Access-Control-Allow-Headers: Content-Type\r\n", "");
            return;
        }
        
        if (mg_http_match_uri(hm, "/api/derby/setup")) {
            handle_setup(c, hm);
        } else if (mg_http_match_uri(hm, "/api/derby/dash")) {
            handle_dash(c, hm);
        } else {
            struct mg_http_serve_opts opts = {.root_dir = "./static"};
            mg_http_serve_dir(c, hm, &opts);
        }
    }
    (void) fn_data;
}

int main(void) {
    struct mg_mgr mgr;
    mg_mgr_init(&mgr);
    srand(time(NULL));
    printf("Starting server on port 6009\n"); 
    mg_http_listen(&mgr, "http://0.0.0.0:6009", fn, NULL);
    for (;;) {
        mg_mgr_poll(&mgr, 1000);
    }
    mg_mgr_free(&mgr);
    return 0;
}