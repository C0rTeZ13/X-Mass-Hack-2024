﻿using System.ComponentModel.DataAnnotations;

namespace API.Models
{
    public class AuthRequest
    {
        [Required]
        public string UserName { get; set; }

        [Required]
        public string Password { get; set; }
    }
}
